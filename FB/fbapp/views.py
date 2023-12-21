from django.shortcuts import render, HttpResponse,redirect
from django.http import FileResponse,JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Q
from django.core.mail import send_mail
from django.template import loader
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
# from django.contrib.sites.models import Site
from django.views.decorators.csrf import csrf_exempt
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.core.cache import cache

import json
import os
import uuid
from random import randint
import pandas as pd
from datetime import datetime,timedelta, date
from pathlib import Path
from passlib.hash import pbkdf2_sha256
import jwt
from .s3_bucket import upload_file
from fbapp.models import *
from .data_export import export_form_to_excel, convert_string_to_date, formnames
from .scraper import article_scrapper
from .decorators import *
from .serializers import *
from .data_import import *




# ======================== Important Variables ==========================
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

pages={'index':'Home Page','category_page':'Category page',
        'brand_page':'Brand Page','fr_directory_page':'Franchise Directory',
        'featured_brands':'Featured Brands','about_us':'About Us',
        'blog':'Blog Page','contact_us':'Contact Us',
        'terms_and_condition':'Terms & Conditions',
        'privacy_and_policy':'Privacy Policy','refund_and_cancellation':'Refund and Cancellation'}


employee_access={
        # 'site_mngt':'Website Management',
        'category_brand_mngt':'Category, Brand Management',
        'blog_article_mngmt':'Blogs, Articles Management','event_mngt':'Event Management',
        # 'featured_brands':'Featured Brands',
        # 'pp_tc_rc':'PP,TC and RC Management',
        'client_data_mngt':'Client Data',
        # 'bots_mngt':'Bots Management'
        }

emptyValuesList=['',' ',None,'#', 'null',0]

# ======================== Important Functions  ==============================================================


def clearRedisCache():
    cache.clear()

def update_upcomming_event_status():
    try:
        for up_event in event.objects.filter(event_status__icontains='yes'):
            if timezone.now() > up_event.event_date:
                up_event.event_status='No'
                up_event.save()
    except:
        pass

def push_notification(From=None,from_role=None,to=None,to_role=None,title=None, description=None, url=None):
    if to==None or title== None or From == None or from_role==None or to_role==None:
        return False, 'user and title should not be null'
    for user in to:
        notification_obj=Notifications(
            notification_title=title,
            notification_from=From,
            notification_from_role=from_role,
            notification_to=user,
            notification_to_role=to_role,
            notification_description=description,
            notification_url=url,
            notification_status=1
            )
        notification_obj.save()
    
    if '?' in notification_obj.notification_url:
        notification_obj.notification_url=notification_obj.notification_url+f'&notification={notification_obj.id}'
    else:
        notification_obj.notification_url=notification_obj.notification_url+f'?notification={notification_obj.id}'
    notification_obj.save()
    return True, 'Notification Created Successfuly'

def update_notification_status(request):
    if 'notification' in request.GET:
        try:
            Notifications.objects.filter(id=request.GET['notification']).update(notification_status=2)
        except:
            pass

def generate_jwt_token(payload):
    exp = datetime.now() + (timedelta(minutes=60) )
    # payload.update({'exp':exp,'iat':datetime.now()})
    payload.update({'exp':exp})
    token = jwt.encode(payload, settings.TOKEN_KEY, algorithm =settings.JWT_ALGORITHM[0]) #.decode('utf-8')
    return token

def generate_otp():
    otp=randint(000000,999999)
    return otp

def get_brand_royalty(brand_obj,):
    royalty=[]
    royalty_type=json.loads(brand_obj.brand_royalty_type)
    royalty_fee=json.loads(brand_obj.brand_royalty_fee)
    for i in range(0,len(json.loads(brand_obj.brand_royalty_type))):
        royalty.append({'royalty_type':royalty_type[i],'royalty_fee': royalty_fee[i]})
    return royalty

def un_authorized_access_handler(request):
    return render(request, 'admin-panel/403.html')

# HTTP Errors handling functions
# HTTP Error 404
def page_not_found(request,exception):
    return render(request, 'front-end/404.html',status=404)
    # return response


def send_alert_msg(request,msg, url):
    return render(request, 'admin-panel/alert.html',{'msg':msg,'redirect_location':url})

def getslug(name):
    return slugify(name+" "+str(uuid.uuid4())[:6])

def get_admin_ids():
    ids=[]
    users=User.objects.all()
    for user in users:
        ids.append(user.id)
    return ids



def is_admin(request):
    try:
        token = request.COOKIES.get('token', None)
        if token!=None:
            try:
                payload = jwt.decode(token, settings.TOKEN_KEY, algorithms=settings.JWT_ALGORITHM)
                if payload['role']=='admin' and payload['access']=='all':
                    return True
                else:
                    return False
            except Exception as e:
                return False
    except Exception as e:
        return False


def get_logged_user_data(request, keys):
    data={}
    try:
        token = request.COOKIES.get('token', None)
        if token!=None:
            try:
                payload = jwt.decode(token, settings.TOKEN_KEY, algorithms=settings.JWT_ALGORITHM)
                for key in keys:
                    try:
                        data.update({key:payload[key]})
                    except:
                        data.update({key:'None'})
                return data
            except Exception as e:
                print('Error: at get_logged_user_data()',str(e))
                return data
    except Exception as e:
        print('Error: at get_logged_user_data()',str(e))
        return data

def move_this_record_to_bin(record_id,record_name,record_category,record_data,logs=None):
    trash_obj=TrashBin(
            record_id=record_id,
            record_name=record_name,
            record_category =record_category,
            record_data =json.dumps(record_data,ensure_ascii=False),
            record_exists_till=timezone.now()+(timedelta(days=15)) )
    if logs !=None:
        trash_obj.logs=json.dumps(logs,ensure_ascii=False)
    trash_obj.save()
    return True

def send_email():
    pass

def test(request):
    # brds=brand.objects.filter(ismasterfran)
    return HttpResponse('Done')
    return render(request, 'admin-panel/test.html')



#====================================================================================================================
#                                              ADMIN / EMPLOYEE VIEWS  
#====================================================================================================================

def logout(request):
    response = redirect('admin_login')
    response.delete_cookie('token')
    return response

def login_view(request):
    try:
        token = request.COOKIES.get('token', None)
        if token!= None:
            return redirect("logout")
    except:
        pass

    if request.method == 'GET':
        return render(request,'admin-panel/login.html')

    if request.method=="POST":
        try:
            if request.POST['role'] == 'admin':
                user=authenticate(request,username=request.POST['uname'],password=request.POST['psw'])
                if user is not None:
                    if user.is_active:
                        token=generate_jwt_token({'role':'admin','id':user.id, 'email':user.email,'firstname':user.first_name,'lastname':user.last_name,'access':'all'})
                        if 'target' in request.POST:
                            response =  redirect(request.POST['target'])
                        else:
                            response =  redirect("admin")
                        response.set_cookie(key='token', value=token, httponly=True)
                        return response
                    else:
                        return render(request,'admin-panel/login.html',{'msg':'Account Disabled Please Contact admin'})
                else:
                    return render(request,'admin-panel/login.html',{'msg':'Invalid Login'})
            
            elif request.POST['role']== 'employee':
                try:
                    employee_obj=Employee.objects.get(email__iexact=request.POST['uname'])
                    if not pbkdf2_sha256.verify(request.POST['psw'],employee_obj.password):
                        return render(request,'admin-panel/login.html',{'msg':'Invalid Password'})
                    else:
                        if employee_obj.is_active == 0 or employee_obj.is_active == '0':
                            return render(request,'admin-panel/login.html',{'msg':'Account Disabled Please Contact admin'})
                        else:
                            token=generate_jwt_token({'id':employee_obj.id,'role':'employee','email':employee_obj.email,'firstname':employee_obj.firstname,'lastname':employee_obj.lastname, 'access':employee_obj.access})
                            if 'target' in request.POST:
                                response =  redirect(request.POST['target'])
                            else:
                                response =  redirect("admin")
                            response.set_cookie(key='token', value=token, httponly=True)
                            return response
                except Employee.DoesNotExist:
                    return render(request,'admin-panel/login.html',{'msg':'Invalid Username'})
                except Exception as e:
                    return render(request,'admin-panel/login.html',{'msg':f'Server Error{str(e)}'})
        except:
            return render(request,'admin-panel/login.html',{'msg':'Invalid Login'})


def forgot_password(request):
    if request.method == 'GET':
        return redirect('admin_login')

    if request.method == 'POST':
        try:
            role=request.POST['role']
            if role == 'employee':
                try:
                    Employee.objects.get(email__iexact = request.POST['uname'])
                    guid=str(uuid.uuid4())+str(uuid.uuid4())
                    try:
                        Reset_Password_Requests.objects.get(email__iexact = request.POST['uname']).delete()
                    except:
                        pass
                    # remove_old_password_requests()
                    rpr=Reset_Password_Requests.objects.create(
                            email       =   request.POST['uname'],
                            token       =   guid,
                            valid_till  =   timezone.make_aware(datetime.now()+(timedelta(minutes=60)))
                        )
                    reseturl=settings.DOMAIN_ADDRS+'/reset-password/?token='+guid+'&id='+str(rpr.id)+'&email='+request.POST['uname']
                    html_message=loader.render_to_string('mail_templates/forgotpassword.html',{'reset_url':reseturl})
                    send_mail("Franchise Brigade:Password reset link",'OTP',settings.EMAIL_HOST_USER,[request.POST['uname']],html_message=html_message,fail_silently=False)
                    return render(request,'admin-panel/login.html',{'msg':'Password reset link has been sent to your email id. Pls Check'})
                except Employee.DoesNotExist:
                    return render(request,'admin-panel/login.html',{'msg':'Invalid Username / Email'})
            else:
                return render(request,'admin-panel/login.html',{'msg':'Forgot password for ADMIN is Under development'})
        except Exception as e:
            print(e)
            return render(request,'admin-panel/login.html',{'msg':'Error Occured'})

def reset_password(request):
    try:
        token=request.GET['token']
        rpr_id=request.GET['id']
        email=request.GET['email']
        rpr_obj=Reset_Password_Requests.objects.filter(id=rpr_id, email__iexact=email).get()
        if token==rpr_obj.token:
            if timezone.make_aware(datetime.now())>rpr_obj.valid_till:
                return render(request, 'admin-panel/reset_password.html',{'status':False,'msg':'Url Expired'})
            else:
                if request.method=='GET':
                    return render(request, 'admin-panel/reset_password.html',{'status':True})
                if request.method == 'POST':
                    emp_obj=Employee.objects.get(email__iexact=email)
                    emp_obj.password=pbkdf2_sha256.hash(request.POST['password'],rounds=1200,salt_size=32)
                    emp_obj.save()
                    rpr_obj.delete()
                    return render(request, 'admin-panel/reset_password.html', {'status':False,'msg':'Password Changed Successfuly','link':'/admin_login'})
        else:
            return render(request, 'admin-panel/reset_password.html',{'status':False,'msg':'Invalid Token'})
    except Exception as e:
        print(e)
        return render(request, 'admin-panel/reset_password.html',{'status':False,'msg':'Invalid Details'})

@check_authentication
def adminindex(request):
    update_notification_status(request)
    return render(request,'admin-panel/index.html')


# ______________________________________ Site management views _________________________________________________
@check_authentication
def update_logo(request):
    if check_authorization(request, permission_key='site_mngt'):
        home_details=Home_Details.objects.get()
        view_category=category.objects.all()
        msg='Logo Updated Successfully'
        context={'home_details':home_details,'view_category':view_category,}
        
        if request.method=="POST":        
            home_details.logo=request.FILES['logo']
            home_details.save()
            url=upload_file("media/images/"+str(request.FILES['logo']).replace(' ','_'), 'franchise-brigade',"media/home_logo.jpg")
            home_details.logo=url
            home_details.save()
            os.remove("media/images/"+str(request.FILES['logo']).replace(' ','_'))
            msg='Logo Updated Successfully'
            clearRedisCache()
            return render(request,'admin-panel/update-logo.html',{'home_details':home_details,'msg':msg})
        return render(request,'admin-panel/update-logo.html',context)  
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def update_banner(request):
    if check_authorization(request, permission_key='site_mngt'):    
        home_details=Home_Details.objects.get()
        view_category=category.objects.all()
        msg='Banner Updated Successfully'
        context={'home_details':home_details,'view_category':view_category,}
        
        if request.method == "POST":
            if 'banner1' in request.FILES.keys():
                home_details.banner1=request.FILES['banner1']
            if 'banner2' in request.FILES.keys():
                home_details.banner2=request.FILES['banner2']
            if 'banner3' in request.FILES.keys():
                home_details.banner3=request.FILES['banner3']
            home_details.save()
            if 'banner1' in request.FILES.keys():
                url=upload_file("media/images/"+str(request.FILES['banner1']).replace(' ','_'), 'franchise-brigade',"media/home_banner/bannerimage1.jpg")
                home_details.banner1=url
                os.remove("media/images/"+str(request.FILES['banner1']).replace(' ','_'))
            if 'banner2' in request.FILES.keys():
                url=upload_file("media/images/"+str(request.FILES['banner2']).replace(' ','_'), 'franchise-brigade',"media/home_banner/bannerimage2.jpg")
                home_details.banner2=url
                os.remove("media/images/"+str(request.FILES['banner2']).replace(' ','_'))
            if 'banner3' in request.FILES.keys():
                url=upload_file("media/images/"+str(request.FILES['banner3']).replace(' ','_'), 'franchise-brigade',"media/home_banner/bannerimage3.jpg")
                home_details.banner3=url
                os.remove("media/images/"+str(request.FILES['banner3']).replace(' ','_'))
            home_details.save()
            clearRedisCache()
            return render(request,'admin-panel/update-banner-img.html',{'msg':msg,'home_details':home_details})        
        return render(request,'admin-panel/update-banner-img.html',context)
    else:
        return un_authorized_access_handler(request)

#@login_required(login_url='/admin_login/')
@check_authentication  
def update_about(request):
    if check_authorization(request, permission_key='site_mngt'):
        view_category=category.objects.all()
        home_details=Home_Details.objects.get()
        update_about_sec=about_sec.objects.get()
        msg="About Section Updated Successfully"
        context={'view_category':view_category,'update_about_sec':update_about_sec,'home_details':home_details,}    
       
        if request.method=="POST":
            update_about_sec.head=request.POST['head']
            update_about_sec.footer_content=request.POST['footer_content']
            update_about_sec.page_content=request.POST['page_content']
            if 'about_banner' in request.FILES.keys():
                update_about_sec.about_banner=request.FILES['about_banner']
            update_about_sec.save()
            if 'about_banner' in request.FILES.keys():
                url=upload_file("media/images/about/"+str(request.FILES['about_banner']).replace(' ','_'),'franchise-brigade',"media/about_banner/about_banner.jpg")
                update_about_sec.about_banner=url
                os.remove("media/images/about/"+str(request.FILES['about_banner']).replace(' ','_'))
            update_about_sec.save()
            clearRedisCache()
            return render(request,'admin-panel/update-about-sec.html',{'msg':msg,'home_details':home_details})
        return render(request,'admin-panel/update-about-sec.html',context)
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def update_contact(request):
    if check_authorization(request, permission_key='site_mngt'):
        home_details=Home_Details.objects.get()
        view_category=category.objects.all()
        msg="Contact Updated Successfully"
        context={'home_details':home_details,'view_category':view_category,}    
        
        if request.method=="POST":
            home_details.Phone=request.POST['Phone']
            home_details.email=request.POST['email']
            home_details.address=request.POST['address']
            home_details.save()
            clearRedisCache()
            return render(request,'admin-panel/update-contact-details.html',{'msg':msg,'home_details':home_details})
        return render(request,'admin-panel/update-contact-details.html',context)
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def update_social(request):
    if check_authorization(request, permission_key='site_mngt'):
        social_data=social_link.objects.get()
        msg="Social Link Updated Successfully"
        context={'social_data':social_data}
        
        if request.method=="POST":
            social_data.youtube=request.POST['youtube']
            social_data.facebook=request.POST['facebook']
            social_data.instagram=request.POST['instagram']
            social_data.linkedin=request.POST['linkedin']
            social_data.whatsup=request.POST['whatsup']
            social_data.save()
            clearRedisCache()
            return render(request,'admin-panel/update-social-links.html',{'msg':msg})
        return render(request,'admin-panel/update-social-links.html',context)
    else:
        return un_authorized_access_handler(request)


# @login_required(login_url='/admin_login/')
@check_authentication
def add_review(request):
    if check_authorization(request, permission_key='site_mngt'):
        msg="Review Added Successfully"
        context={}
        if request.method == "POST":
            #for adding video only
            if 'review_video' in request.FILES.keys():
                video=request.FILES['review_video'].read()
                path1="media/images/review_videof/"+str(request.FILES['review_video']).replace(' ','_')
                f=open(path1,'wb+')
                f.write(video)
                f.close()
                url1=upload_file(path1,'franchise-brigade',path1)
                os.remove(path1)
                review_video=url1
                review.objects.create(review_name='',review_content='',review_image='',review_status='',review_video=review_video,text_review=False)
                return render(request,'admin-panel/add-review.html',{'msg':msg})
            # for adding text review only
            review_name=request.POST['review_name']
            review_content=request.POST['review_content']
            review_status=request.POST['review_status']   
            # review_video=request.FILES['review_video']
            
            if 'review_image' in request.FILES.keys():
                image=request.FILES['review_image'].read()
                path="media/images/review/"+str(request.FILES['review_image']).replace(' ','_')
                f=open(path,'wb+')
                f.write(image)
                f.close()
                url=upload_file(path,'franchise-brigade',"media/review_image/"+str(request.POST['review_name'])+".jpg")
                os.remove(path) 
            else:
                url=''
            url=""
            review_video=url1
            review_image=url
            review.objects.create(review_name=review_name,review_content=review_content,review_image=review_image,review_status=review_status,review_video=review_video,text_review=True)
            clearRedisCache()
            return render(request,'admin-panel/add-review.html',{'msg':msg})
        return render(request,'admin-panel/add-review.html',context)
    else:
        return un_authorized_access_handler(request)


# _________________________________________ Privacy, Terms and Cancelation, Refund views _____________________________________
@check_authentication
def update_privecy_policy(request):
    if check_authorization(request, permission_key='pp_tc_rc'):
        home_details=Home_Details.objects.get()
        msg="Privacy Policy Updated Successfully"
        context={'home_details':home_details}
        
        if request.method=="POST":
            home_details.pp=request.POST['pp']
            home_details.save()
            clearRedisCache()
            return render(request,'admin-panel/update-privacy-policy.html',{'msg':msg,'home_details':home_details})
        return render(request,'admin-panel/update-privacy-policy.html',context)
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def update_terms_condition(request):
    if check_authorization(request, permission_key='pp_tc_rc'):
        home_details=Home_Details.objects.get()
        msg="Terms & Conditions Updated Successfully"
        context={'home_details':home_details}
        
        if request.method=="POST":
            home_details.tc=request.POST['tc']
            home_details.save()
            clearRedisCache()
            return render(request,'admin-panel/update-terms-and-conditions.html',{'msg':msg,'home_details':home_details})
        return render(request,'admin-panel/update-terms-and-conditions.html',context)
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def update_refund_cancellition(request):
    if check_authorization(request, permission_key='pp_tc_rc'):
        home_details=Home_Details.objects.get()
        msg="Refund & Cancellition Updated Successfully"
        context={'home_details':home_details}
        if request.method=="POST":
            home_details.rc=request.POST['rc']
            home_details.save()
            clearRedisCache()
            return render(request,'admin-panel/update-refund-and-cancellation.html',{'msg':msg,'home_details':home_details})
        return render(request,'admin-panel/update-refund-and-cancellation.html',context)
    else:
        return un_authorized_access_handler(request)


# ___________________________________________ Blogs and Article views ______________________________________________________________
@check_authentication
def add_blog(request):
    if check_authorization(request, permission_key='blog_article_mngmt'):
        if request.method=='GET':
            return render(request,'admin-panel/add-blog.html')
        
        if request.method == "POST":
            data={}
            user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id'])            
            fields=BlogSerializer().data.keys()
            
            for field in fields:
                try:
                    if field in request.POST:
                        if request.POST[field] not in emptyValuesList:
                            data[field]=request.POST[field]
                except Exception as e:
                    print('ERROR:\nfile_name',__file__+'\nerror:'+str(e)+'\n')
            
            if 'blog_image' in request.FILES.keys():
                image=request.FILES['blog_image'].read()
                path="media/images/blog/"+str(request.FILES['blog_image']).replace(' ','_')
                f=open(path,'wb+')
                f.write(image)
                f.close()
                url=upload_file(path,'franchise-brigade',"media/blog_image/"+str(request.POST['blog_title']).replace(' ','_')+".jpg")
                # os.remove(path)
            else:
                url=""
            data['blog_image']=url
            data['blog_slug']=getslug(data['blog_title'])
            
            # logs=[{ "action_type":"insert", "requested_by":user_data['firstname']+' '+user_data['lastname'], "requested_user_id":user_data['id'],
            #         "requested_at":str(timezone.now())}]
            
            if is_admin(request):
                msg='Blog Data Added Successfuly'
                # logs[0].update({"response_by":user_data['firstname']+' '+user_data['lastname'], "response_user_id":user_data['id'], "responsed_at":str(timezone.now()),"update_data":[]})
                # data['logs']=json.dumps(logs)
                blog.objects.create(**data) #blog_title=blog_title,blog_content=blog_content,blog_image=blog_image)
                clearRedisCache()
            else:
                msg='A request has been sent to Admin'
                # data['logs']=json.dumps(logs)
                data['actor']=user_data['id']
                tblog=Temp_Blog.objects.create(**data)
                push_notification(From=user_data['id'],from_role='employee',to=get_admin_ids(),to_role='admin',
                                 title=f"Blog - insert request by {user_data['firstname']}", url=f"/approval-requests?for=blog&id={tblog.id}" )
            return render(request, 'admin-panel/alert.html',{'msg':msg,'redirect_location':'/add-blog'})
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def update_all_blog(request):
    if check_authorization(request, permission_key='blog_article_mngmt'):
        blog_data=blog.objects.all().order_by('-id')
        context={'blog_data':blog_data}
        return render(request,'admin-panel/update-blog.html',context)
    else:
        return un_authorized_access_handler(request)


@check_authentication
def update_single_blog(request,pk):
    if check_authorization(request, permission_key='blog_article_mngmt'):
        blog_data=blog.objects.get(id=pk)
        context={'blog_data':blog_data,'pk':pk}
        
        if request.method=='GET':
            return render(request,'admin-panel/update-single-blog.html',context)
        
        if request.method == "POST":
            fields=BlogSerializer().data.keys()
            data=request.POST.dict() 
            user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id'])            
            
            # if 'blog_image' in request.FILES.keys():
            #     data['blog_image']=request.FILES['blog_image']
            
            if 'blog_image' in request.FILES.keys():
                image=request.FILES['blog_image'].read()
                path="media/images/blog/"+str(request.FILES['blog_image']).replace(' ','_')
                f=open(path,'wb+')
                f.write(image)
                f.close()
                # url=upload_file(path,'franchise-brigade',"media/blog_image/"+str(request.POST['blog_title']).replace(' ','_')+".jpg")
                url=upload_file(path,'franchise-brigade',"media/blog_image/"+str(blog_data.blog_image).replace(' ','_')+".jpg")
                data['blog_image']=url
                os.remove(path)
            
            if 'blog_title' in data:
                data['blog_slug']=getslug(data['blog_title'])
            
            if is_admin(request):
                for field in fields:
                    try:
                        if field in data:
                            if data[field] not in emptyValuesList:
                                blog_data.__dict__.update({field:data[field]})
                    except Exception as e:
                        print('ERROR:\nfile_name',__file__+'\nerror:'+str(e)+'\n')
                blog_data.save()
                clearRedisCache()
                return JsonResponse({"msg":f"Blog data updated successfuly",'status':True})
            else:
                tblog_data={}
                for field in fields:
                    try:
                        if field in data:
                            if data[field] not in emptyValuesList:
                                tblog_data[field]=data[field]
                    except Exception as e:
                        print('ERROR:\nfile_name',__file__+'\nerror:'+str(e)+'\n')
                tc_obj=Temp_Blog.objects.create(**tblog_data)
                tc_obj.task_type='update'
                tc_obj.to_blog_id=blog_data.id
                tc_obj.actor=user_data['id']
                tc_obj.save()
                push_notification(From=user_data['id'],from_role='employee',to=get_admin_ids(),to_role='admin',
                                 title=f"Blog - update request by {user_data['firstname']}", url=f"/approval-requests?for=blog&id={tc_obj.id}" )
                return JsonResponse({"msg":"Blog data updated  request sent to admin",'status':True})
    else:
        return un_authorized_access_handler(request)

@check_authentication
def delete_blog(request, pk):
    if check_authorization(request, permission_key='blog_article_mngmt'):
        blog_data=blog.objects.get(id=pk)
        user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id'])            
        
        if is_admin(request):
            try:
                move_this_record_to_bin(blog_data.id,blog_data.blog_title,'blog',BlogSerializer(blog_data).data,logs=None)
                blog_data.delete()
                clearRedisCache()
                msg='Blog data deleted successfuly'
                return send_alert_msg(request, msg,'/update-blog/')
            except Exception as e:
                return redirect("/admin/")
        else:
            msg='A request has been sent to Admin'
            # user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id'])
            # # cat_logs=json.loads(cat.logs)
            # logs=[{ "action_type":"delete", "requested_by":user_data['firstname']+' '+user_data['lastname'], "requested_user_id":user_data['id'],
            #         "requested_at":str(timezone.now()),"response_by":"", "response_user_id":"", "responsed_at":"","update_data":[]}]
            # cat_logs.append(logs)
            tblog=Temp_Blog.objects.create(
                    task_type       =   'delete',
                    to_blog_id  =   blog_data.id,
                    actor           =  user_data['id'])
                    # logs            =   json.dumps(logs))
            push_notification(From=user_data['id'],from_role='employee',to=get_admin_ids(),to_role='admin',
                                 title=f"Blog - delete request by {user_data['firstname']}", url=f"/approval-requests?for=blog&id={tblog.id}" )
            return send_alert_msg(request, msg,'/update-blog/')
    else:
        return un_authorized_access_handler(request)

@check_authentication
def add_article(request):
    if check_authorization(request, permission_key='blog_article_mngmt'):
        # home_details=Home_Details.objects.get()
        # view_category=category.objects.all()
        context={}

        if request.method == 'GET':
            return render(request,'admin-panel/add-article.html',context)
        
        if request.method == "PUT":
            try:
                url=request.GET['url']
                resp=article_scrapper(url)
                if resp['status']:
                    resp.update({"msg":"Data fetched"})
                    response=JsonResponse(resp)
                else:
                    response=JsonResponse({'status':False,"msg":"Error Occured while fetching"})
            except KeyError:
                response=JsonResponse({'status':False,"msg":"Error Occured while fetching"})
            return response

        if request.method == "POST":
            if 'article_image' in request.FILES.keys():
                image=request.FILES['article_image'].read()
                path="media/images/article_image/"+str(request.FILES['article_image']).replace(' ','_')
                f=open(path,'wb+')
                f.write(image)
                f.close()
                url=upload_file(path,'franchise-brigade',"media/article_image/"+str(request.POST['article_scraped_title']).replace(' ','_')+".jpg")
                # os.remove(path)
            else:
                url=request.POST['article_scraped_img_url']
            article_image=url
            article_obj=Articles(
                article_title=request.POST['article_scraped_title'],
                article_slug=getslug(request.POST['article_scraped_title']),
                article_url=request.POST['article_url'],
                article_desc=request.POST['article_scraped_description'],
                article_img=article_image
            )
            article_obj.save()
            clearRedisCache()
            return render(request, 'admin-panel/alert.html',{'msg':'Article Added Successfuly',' redirect_location':'/add-article'})
    else:
        return un_authorized_access_handler(request)


@check_authentication
def delete_article(request):
    if check_authorization(request, permission_key='blog_article_mngmt'):
        try:
            try:
                article_id=request.GET['id']
                thisarticle=Articles.objects.filter(id=article_id).get()
                thisarticle.delete()
                clearRedisCache()
                articles=Articles.objects.all()
                return redirect("/delete-article")
            except KeyError:
                articles=Articles.objects.all()
                # push_notification(user=1, title='Mani Sharma Musicals', description="Gottu", url='/add-bot')
                return render(request,'admin-panel/update-article.html',{'articles':articles})
        except:
            return redirect("/admin/")
    else:
        return un_authorized_access_handler(request)


# _______________________________________________  Event Views ________________________________________________________________
# @login_required(login_url='/admin_login/')
@check_authentication
def add_event(request):
    if check_authorization(request, permission_key='event_mngt'):
        msg="Event Addeded Successfully"
        context={}
        
        if request.method == "POST":
            event_title=request.POST['event_title']
            event_content=request.POST['event_content']
            event_status=request.POST['event_status']
            event_date=request.POST['event_date']
            event_url=request.POST['event_url']
            pre_event_image=[]
            if 'pre_event_image[]' in request.FILES.keys():
                i=0
                for j in request.FILES.getlist('pre_event_image[]'):
                    path1="media/images/event/"+str(j).replace(' ','_')
                    image=j.read()
                    f=open(path1,'wb+')
                    f.write(image)
                    f.close()
                    url=upload_file(path1,'franchise-brigade',"media/images/event/"+str(request.POST['event_title']).replace(' ','_')+'_'+str(i)+".jpg")
                    os.remove(path1)
                    pre_event_image.append(url)
                    i=int(i)+1
            if 'event_image' in request.FILES.keys():
                image=request.FILES['event_image'].read()
                path="media/images/event/"+str(request.FILES['event_image']).replace(' ','_')
                f=open(path,'wb+')
                f.write(image)
                f.close()
                url=upload_file(path,'franchise-brigade',"media/event_image/"+str(request.POST['event_title'])+".jpg")
                os.remove(path)       
            else:
                url=""
            event_image=url
            event.objects.create(event_title=event_title,event_content=event_content,event_image=event_image,event_status=event_status,event_url=event_url,event_date=event_date,pre_event_image=json.dumps(pre_event_image))
            clearRedisCache()
            return render(request,'admin-panel/add-event.html',{'msg':msg}) 

        return render(request,'admin-panel/add-event.html',context)
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def update_all_event(request):
    if check_authorization(request, permission_key='event_mngt'):
        event_data=event.objects.all()
        context={'pre_event_data':event_data.filter(event_status='No'),'up_event_data':event_data.filter(event_status='Yes')}
        return render(request,'admin-panel/update-event.html',context)
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def update_single_event(request,pk):
    if check_authorization(request, permission_key='event_mngt'):   
        event_data=event.objects.get(id=pk)
        msg="Event Updated Successfully"
        context={'event_data':event_data,'pk':pk,}
        if request.GET.get('action')=='delete':
            event_data.delete()
            msg='Event Deleted Succesfuly'
            return render(request, 'admin-panel/alert.html',{'msg':msg,'redirect_location':'/update-event/'})
        
        if 'confirm' in request.POST.keys():
            if request.POST['confirm']=='DELETE':
                event_data.delete()
                return redirect('/update-event/',{'msg':msg})
        if request.method == "POST":        
            event_data.event_title=request.POST['event_title']
            event_data.event_content=request.POST['event_content']
            event_data.event_date=request.POST['event_date']
            event_data.event_url=request.POST['event_url']
            if 'event_image' in request.FILES.keys():
                image1=request.FILES['event_image'].read()
                path1="media/images/event/"+str(request.FILES['event_image']).replace(' ','_')
                f=open(path1,'wb+')
                f.write(image1)
                f.close()
                
                url1=upload_file(path1,'franchise-brigade',"media/event/"+str(request.POST['event_title'])+".jpg")
                os.remove(path1)
                event_data.event_image=url1
            # else:
                # url1=""
            # event_data.event_image=url1
            event_data.save()
            clearRedisCache()
            
            return render(request,'admin-panel/update-upcoming-event.html',{'msg':msg,'event_data':event_data})    
        return render(request,'admin-panel/update-upcoming-event.html',context)
    else:
        return un_authorized_access_handler(request)


# @login_required(login_url='/admin_login/')
@check_authentication
def update_single_pre_event(request,ppk):
    if check_authorization(request, permission_key='event_mngt'):
        pre_event_data=event.objects.get(id=ppk)
        msg="Event Updated Successfully"
        all_pre_event_img=json.loads(pre_event_data.pre_event_image)
        context={'pre_event_data':pre_event_data,'pre_event_data_img':all_pre_event_img}
        
        if 'confirm' in request.POST.keys():
            if request.POST['confirm']=='DELETE':
                pre_event_data.delete()
                return redirect('/update-event/',{'msg':msg})
            # else :
            #     return render(request,'admin-panel/update-upcoming-event.html',{'msg':msg,'home_details':home_details})
        if request.method == "POST":  
            if 'delete_image' in request.POST.keys():
                gallery=json.loads(pre_event_data.pre_event_image)
                gallery.remove(request.POST['delete_image'])
                pre_event_data.pre_event_image=json.dumps(gallery)
                pre_event_data.save()            
                return redirect('update_single_pre_event',ppk)    

            pre_event_data.event_title=request.POST['event_title']
            pre_event_data.event_content=request.POST['event_content']
            pre_event_data.event_date=request.POST['event_date']  
            if 'pre_event_image[]' in request.FILES.keys():
                # print(request.FILES.getlist('pre_event_image[]'))
                gallery=json.loads(pre_event_data.pre_event_image)
                # print(gallery)
            
                # print(gallery)
                i=len(gallery)-1
                for p in request.FILES.getlist('pre_event_image[]'):
                    # print(p)
                    path="media/images/event/"+str(p).replace(' ','_')
                    image=p.read()
                    f=open(path,'wb+')
                    f.write(image)
                    f.close()
                    url=upload_file(path,'franchise-brigade',"media/evetnt_image/"+str(request.POST['event_title']).replace(' ','_')+'_'+str(i)+".jpg")
                    os.remove(path)
                    gallery.append(url)
                    i=i+1
                # print(gallery)
                pre_event_data.pre_event_image=json.dumps(gallery)
            # pre_event_data.brand_logo=request.FILES['brand_logo']
            # print(request.FILES)

            if 'event_image' in request.FILES.keys():
                image1=request.FILES['event_image'].read()
                path1="media/images/event/"+str(request.FILES['event_image']).replace(' ','_')
                
                
                f=open(path1,'wb+')
                f.write(image1)
                f.close()
                
                url1=upload_file(path1,'franchise-brigade',"media/event/"+str(request.POST['event_title'])+".jpg")
                os.remove(path1)
            # else:
                
            #     url1=""
            pre_event_data.event_image=url1
            # print(url1)
            pre_event_data.save()
            clearRedisCache()
            # print(type(json.loads(pre_event_data.pre_event_image)))

            return render(request,'admin-panel/update-previous-event.html',context) 
            
        return render(request,'admin-panel/update-previous-event.html',context)
    else:
        return un_authorized_access_handler(request)


# ___________________________________________ Category , Brand, Non-exclusive brand Management ___________________________________________
@check_authentication
def add_category(request):
    if check_authorization(request, permission_key='category_brand_mngt'):
        msg="Category Added Successfully"
        context={}
        
        if request.method == 'GET':
            return render(request,'admin-panel/add-category.html',context)
        
        if request.method== 'POST':
            data={}
            user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id'])            
            fields=CategorySerializer().data.keys()

            for field in fields:
                try:
                    if field in request.POST:
                        if request.POST[field] not in ['',' ',None]:
                            data[field]=request.POST[field]
                except Exception as e:
                    print('ERROR:\nfile_name',__file__+'\nerror:'+str(e)+'\n')
                    # continue

            if 'category_banner_image' and 'category_home_image' in request.FILES.keys():
                image=request.FILES['category_banner_image'].read()
                image1=request.FILES['category_home_image'].read()
                path="media/images/category/"+str(request.FILES['category_banner_image']).replace(' ','_')
                path1="media/images/category/"+str(request.FILES['category_home_image']).replace(' ','_')
                f=open(path,'wb+')
                f.write(image)
                f.close()
                f=open(path1,'wb+')
                f.write(image1)
                f.close()
                url=upload_file(path,'franchise-brigade',"media/category_image/"+str(request.POST['category_name']).replace(' ','_')+"_banner.jpg")
                # os.remove(path)
                url1=upload_file(path1,'franchise-brigade',"media/category_image/"+str(request.POST['category_name']).replace(' ','_')+"_home.jpg")
                # os.remove(path1)
            else:
                url=""
                url1=""
            category_banner_image=url
            category_home_image=url1
            
            # if 'category_banner_image' in data:
            data['category_banner_image']=category_banner_image
            # if 'category_home_image' in data:
            data['category_home_image']=category_home_image
            data['category_slug']=getslug(data['category_name'])

            logs=[{ "action_type":"insert", "requested_by":user_data['firstname']+' '+user_data['lastname'], "requested_user_id":user_data['id'],
                    "requested_at":str(timezone.now())}]
            
            if is_admin(request):
                msg='Category Data Added Successfuly'
                logs[0].update({"response_by":user_data['firstname']+' '+user_data['lastname'], "response_user_id":user_data['id'], "responsed_at":str(timezone.now()),"update_data":[]})
                data['logs']=json.dumps(logs)
                print('\n\n',data,'\n\n')
                category.objects.create(**data)
                clearRedisCache()
            else:
                msg='A request has been sent to Admin'
                logs[0].update({"response_by":"", "response_user_id":"", "responsed_at":"","update_data":[]})                
                data['logs']=json.dumps(logs)
                data['actor']=user_data['id']
                tc=Temp_Category.objects.create(**data)
                push_notification(From=user_data['id'],from_role='employee',to=get_admin_ids(),to_role='admin',
                                 title=f"Category - insert request by {user_data['firstname']}", url=f"/approval-requests?for=category&id={tc.id}" )
            
            return render(request, 'admin-panel/alert.html',{'msg':msg,'redirect_location':'/add_category/'})
    else:
        return un_authorized_access_handler(request)

@check_authentication
def delete_category(request):
    if check_authorization(request, permission_key='category_brand_mngt'):
        cat_id=request.GET['id']
        cat=category.objects.get(id=cat_id)
        user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id'])
        if is_admin(request):
            try:
                logs=[{ "action_type":"delete", "requested_by":user_data['firstname']+' '+user_data['lastname'], "requested_user_id":user_data['id'],"requested_at":str(timezone.now())}]       
                brands=brand.objects.filter(category_id=cat).all()
                nebs=NonExclusiveBrands.objects.filter(category_id=cat.id).all()
                for b in brands:
                    move_this_record_to_bin(brand.id,brand.brand_name,'brand',BrandSerializer(b).data,logs)
                for neb in nebs:
                    move_this_record_to_bin(neb.id,neb.brand_name,'non_exclusive_brand',NonExclusiveBrandSerializer(neb).data,logs)
                move_this_record_to_bin(cat.id,cat.category_name,'category',CategorySerializer(cat).data,logs)
                brands.delete()
                nebs.delete()
                cat.delete()
                clearRedisCache()
                msg='Category and its associated brands, Non exclusive brands are deleted successfuly'
                return render(request, 'admin-panel/alert.html',{'msg':msg,'redirect_location':'/admin'})
            except Exception as e:
                print(e)
                return redirect("/admin/")
        else:
            msg='A request has been sent to Admin'
            # user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id'])
            # cat_logs=json.loads(cat.logs)
            logs=[{ "action_type":"delete", "requested_by":user_data['firstname']+' '+user_data['lastname'], "requested_user_id":user_data['id'],
                    "requested_at":str(timezone.now()),"response_by":"", "response_user_id":"", "responsed_at":"","update_data":[]}]
            # cat_logs.append(logs)
            tc=Temp_Category.objects.create(
                    task_type       =   'delete',
                    to_category_id  =   cat.id,
                    actor           =  user_data['id'],
                    logs            =   json.dumps(logs))
            push_notification(From=user_data['id'],from_role='employee',to=get_admin_ids(),to_role='admin',
                                 title=f"Category - delete request by {user_data['firstname']}", url=f"/approval-requests?for=category&id={tc.id}" )
            return render(request, 'admin-panel/alert.html',{'msg':msg,'redirect_location':'/admin'})
            
    else:
        return un_authorized_access_handler(request)

@check_authentication
def update_category(request,pk):
    if check_authorization(request, permission_key='category_brand_mngt'):
        update_notification_status(request)

        edit_category=category.objects.get(pk=pk)
        edit_brand=brand.objects.filter(category_id=pk)
        edit_brand_neb=NonExclusiveBrands.objects.filter(category_id=pk)

        context={'edit_category':edit_category,'edit_brand':edit_brand,'edit_brand_neb':edit_brand_neb,}

        if request.method=="POST":
            data=request.POST.dict()
            user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id'])            

            fields=CategorySerializer().data.keys()
            
            if 'category_name' in data:
                data['category_slug']=getslug(data['category_name'])
            
            logs={ "action_type":"update", "requested_by":user_data['firstname']+' '+user_data['lastname'], "requested_user_id":user_data['id'],
                    "requested_at":str(timezone.now())}
            
            log_previous_values=[]
            log_fields=[]
            log_updated_values=[]
            # logs_update_data=[]

            # for field in fields:
            #     try:
            #         if field in data:
            #             if data[field] != '':
            #                 log_previous_values.append(edit_category.__getattribute__(field))
            #                 log_fields.append(field)
            #                 edit_category.__dict__.update({field:data[field]})
            #                 log_updated_values.append(edit_category.__getattribute__(field))
            #     except Exception as e:
            #         print('ERROR:\nfile_name',__file__+'\nerror:'+str(e)+'\n')
            
            # print(log_fields)
            # print(log_previous_values)
            # print(log_updated_values)
            # return HttpResponse('hi')
            
            # edit_category.save()
            if 'category_banner_image' in request.FILES.keys():
                image=request.FILES['category_banner_image'].read()
                path="media/images/category/"+str(request.FILES['category_banner_image']).replace(' ','_')
                f=open(path,'wb+')
                f.write(image)
                f.close()   
                url=upload_file(path,'franchise-brigade',"media/category_banner_image/"+str(edit_category.category_name).replace(' ','_')+"_banner.jpg")
                data['category_banner_image']=url
                os.remove(path)
            if 'category_home_image' in request.FILES.keys():
                image=request.FILES['category_home_image'].read()
                path="media/images/category/"+str(request.FILES['category_home_image']).replace(' ','_')
                f=open(path,'wb+')
                f.write(image)
                f.close()
                url1=upload_file(path,'franchise-brigade',"media/category_home_image/"+str(edit_category.category_name).replace(' ','_')+"_home.jpg")
                data['category_home_image']=url1
                os.remove(path)

            if is_admin(request):
                for field in fields:
                    try:
                        if field in data:
                            if data[field] not in ['', ' ', None]:
                                temp_data={}
                                temp_data['field']=field
                                temp_data['previous_value']=edit_category.__getattribute__(field)
                                # log_previous_values.append()
                                # log_fields.append(field)
                                edit_category.__dict__.update({field:data[field]})
                                temp_data['new_value']=edit_category.__getattribute__(field)
                                # logs_update_data.append(temp_data)
                    except Exception as e:
                        print('ERROR:\nfile_name',__file__+'\nerror:'+str(e)+'\n')
                
                msg='Category Data Updated Successfuly'
                # logs.update({"response_by":user_data['firstname']+' '+user_data['lastname'], "response_user_id":user_data['id'], "responsed_at":str(timezone.now()),"update_data":logs_update_data})
                # current_logs=json.loads(edit_category.logs)
                # current_logs.append(logs)
                # edit_category.logs=json.dumps(current_logs)
                edit_category.save()
                clearRedisCache()
                return JsonResponse({"msg":f"Category data updated successfuly",'status':True})
            else:
                tc_data={}
                for field in fields:
                    try:
                        if field in data:
                            if data[field] not in ['', ' ', None]:
                                temp_data={}
                                temp_data['field']=field
                                temp_data['previous_value']=edit_category.__getattribute__(field)
                                temp_data['new_value']=data[field]
                                # log_fields.append(field)
                                tc_data[field]=data[field]
                                # logs_update_data.append(temp_data)
                                # edit_category.__dict__.update({field:data[field]})
                                # log_updated_values.append(data[field])
                    except Exception as e:
                        print('ERROR:\nfile_name',__file__+'\nerror:'+str(e)+'\n')
                
                msg='A request has been sent to Admin'
                logs.update({"response_by":"", "response_user_id":"", "responsed_at":"","update_data":'logs_update_data'})                
                tc_obj=Temp_Category.objects.create(**tc_data)
                tc_logs=[logs,]
                tc_obj.logs=json.dumps(tc_logs)
                tc_obj.task_type='update'
                tc_obj.to_category_id=edit_category.id
                tc_obj.actor=user_data['id']
                tc_obj.save()
                push_notification(From=user_data['id'],from_role='employee',to=get_admin_ids(),to_role='admin',
                                 title=f"Category - update request by {user_data['firstname']}", url=f"/approval-requests?for=category&id={tc_obj.id}" )
                return JsonResponse({"msg":f"Category data updated  request sent to admin",'status':True})
        return render(request,'admin-panel/update-category.html',context)
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def update_brand(request,bk):
    if check_authorization(request, permission_key='category_brand_mngt'):
        category_data=category.objects.all()
        edit_brand=brand.objects.get(pk=bk)
        royalty=[]
        royalty_type=json.loads(edit_brand.brand_royalty_type)
        royalty_fee=json.loads(edit_brand.brand_royalty_fee)
        for i in range(0,len(json.loads(edit_brand.brand_royalty_type))):
            royalty.append({
                'royalty_type':royalty_type[i],
                'royalty_fee': royalty_fee[i]
            })
        context={
            'category_data':category_data,
            'edit_brand':edit_brand,
            'gallery':json.loads(edit_brand.brand_gallery),
            'royalty':royalty,}
        
        if request.method=="GET":
            return render(request,'admin-panel/update-brand.html',context)
        
        if request.method=="POST":
            update_data={}

            fields=BrandSerializer().data.keys()
            user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id'])            
            
            for field in fields:
                try:
                    if field in request.POST:
                        if request.POST[field] not in emptyValuesList:
                            update_data[field]=request.POST[field]
                except Exception as e:
                    print('ERROR:\nfile_name',__file__+'\nerror:'+str(e)+'\n')
            
            if 'brand_name' in update_data:
                update_data['brand_slug']=getslug(update_data['brand_name'])

            if 'delete_image' in request.POST.keys():
                gallery=json.loads(edit_brand.brand_gallery)
                gallery.remove(request.POST['delete_image'])
                update_data['brand_gallery']=json.dumps(gallery)

            if 'brand_royalty_type[]' in request.POST:
                update_data['brand_royalty_type']=json.dumps(request.POST.getlist('brand_royalty_type[]'))
            if 'brand_royalty_fee[]' in request.POST:
                update_data['brand_royalty_fee']=json.dumps(request.POST.getlist('brand_royalty_fee[]'))

            # MASTER FRANCHAISE
            if 'brand_ismasterfranchaise' in request.POST:
                update_data['brand_ismasterfranchaise']=request.POST['brand_ismasterfranchaise']
                if update_data['brand_ismasterfranchaise'] == 'no': 
                    update_data['brand_master_investment_min']=0
                    update_data['brand_master_investment_max']=0

            if 'brand_gallery[]' in request.FILES.keys():
                # print(request.FILES.getlist('brand_gallery[]'))
                gallery=json.loads(edit_brand.brand_gallery)
                # print(gallery)
                # x = re.sub("'", " ", gallery)

                # x = re.sub(",", "", x)

                # x = re.split("\s", x)
                # x.remove('[')
                # x.remove(']')
                # for i in x:
                #     if i=='':
                #         x.remove(i)

                # gallery=x

                # print(gallery)
                i=len(gallery)-1
                for p in request.FILES.getlist('brand_gallery[]'):
                    # print(p)
                    path="media/images/brand/"+str(p).replace(' ','_')
                    image=p.read()
                    f=open(path,'wb+')
                    f.write(image)
                    f.close()
                    url=upload_file(path,'franchise-brigade',"media/brand_image/"+str(edit_brand.brand_name).replace(' ','_')+'_'+str(i)+".jpg")
                    os.remove(path)
                    gallery.append(url)
                    i=i+1
                # print(gallery)
                update_data['brand_gallery']=json.dumps(gallery)

            if 'brand_logo' in request.FILES.keys():
                image1=request.FILES['brand_logo'].read()
                path1="media/images/brand/"+str(request.FILES['brand_logo']).replace(' ','_')
                f=open(path1,'wb+')
                f.write(image1)
                f.close()
                update_data['brand_logo']=upload_file(path1,'franchise-brigade',"media/brand_image/"+str(edit_brand.brand_name).replace(' ','_')+"_logo.jpg")
                os.remove(path1)
            
            if 'category_id' in request.POST:
                update_data['category_id']=category.objects.get(id=request.POST['category_id'])
            
            logs={ "action_type":"update", "requested_by":user_data['firstname']+' '+user_data['lastname'], "requested_user_id":user_data['id'],
                    "requested_at":str(timezone.now())}
            
            if is_admin(request):
                for field, value in update_data.items():
                    edit_brand.__dict__.update({field:value})
                msg='Brand Data Updated Successfuly'
                logs.update({"response_by":user_data['firstname']+' '+user_data['lastname'], "response_user_id":user_data['id'], "responsed_at":str(timezone.now())})
                edit_brand.save()
                clearRedisCache()
                return JsonResponse({"msg":f"Brand data updated successfuly",'status':True})
            else:
                msg="A request has sent to admin"
                temp_brand_obj=Temp_Brand.objects.create(**update_data)
                temp_brand_obj.task_type='update'
                temp_brand_obj.to_brand_id=edit_brand.id
                temp_brand_obj.actor=user_data['id']
                temp_brand_obj.save()
                push_notification(From=user_data['id'],from_role='employee',to=get_admin_ids(),to_role='admin',
                                 title=f"Brand - update request by {user_data['firstname']}", url=f"/approval-requests?for=brand&id={temp_brand_obj.id}" )
                return JsonResponse({"msg":f"Brand data updated  request sent to admin",'status':True})
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def delete_brand(request):
    if check_authorization(request, permission_key='category_brand_mngt'):
        brand_id=request.GET['id']
        user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id'])
        
        try:
            bd=brand.objects.filter(id=brand_id).get()
            if is_admin(request):
                logs=[{ "action_type":"delete", "requested_by":user_data['firstname']+' '+user_data['lastname'], "requested_user_id":user_data['id'],"requested_at":str(timezone.now())}]       
                move_this_record_to_bin(bd.id,bd.brand_name,'brand',BrandSerializer(bd).data,logs)
                cat_id=bd.category_id
                bd.delete()
                clearRedisCache()
                return send_alert_msg(request,msg,f"/update_category/{cat_id.id}")
            else:
                msg='A request has been sent to Admin'
                logs=[{ "action_type":"delete", "requested_by":user_data['firstname']+' '+user_data['lastname'], "requested_user_id":user_data['id'],
                        "requested_at":str(timezone.now()),"response_by":"", "response_user_id":"", "responsed_at":"","update_data":[]}]
                tb=Temp_Brand.objects.create(
                        task_type='delete',
                        to_brand_id=bd.id,
                        actor=user_data['id'],
                        logs=json.dumps(logs))
                push_notification(From=user_data['id'],from_role='employee',to=get_admin_ids(),to_role='admin',
                                    title=f"Brand - delete request by {user_data['firstname']}", url=f"/approval-requests?for=brand&id={bd.id}" )
                return send_alert_msg(request,msg,f"/admin")
        except Exception as e:
            print(e)
            return redirect("/admin/")
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def update_non_exclusive_brand(request,bk):
    if check_authorization(request, permission_key='category_brand_mngt'):
        category_data=category.objects.all()
        # brand_data=brand.objects.all(pk=bk)
        
        edit_brand=NonExclusiveBrands.objects.get(pk=bk)
        context={'category_data':category_data,'edit_brand':edit_brand}
        
        if request.method == "GET":
            return render(request,'admin-panel/update-non-exclusive-brand.html',context)
            
        if request.method=="POST":
            # print(request.POST)
            if 'Delete_category' in request.POST.keys() and request.POST['Delete_category']!= '':
                # print('detele category')
                if request.POST['Delete_category']=='DELETE':
                    edit_brand.delete()
                    return redirect('/admin/')
                else :
                    return HttpResponse('Please enter DELETE')
            # print('cat id here ', request.POST['category_id'])
            edit_brand.brand_name=request.POST['brand_name']
            # edit_brand.brand_slug
            edit_brand.category_id=request.POST['category_id']
            edit_brand.brand_outlets=request.POST['brand_outlets']
            edit_brand.yr_of_establish=request.POST['brand_since']
            edit_brand.brand_inv_min=request.POST['brand_inv_min']
            edit_brand.brand_inv_min_type=request.POST['brand_inv_min_type']
            edit_brand.brand_inv_max=request.POST['brand_inv_max']
            edit_brand.brand_inv_max_type=request.POST['brand_inv_max_type']
            edit_brand.brand_payback_min=request.POST['brand_payback_min']
            edit_brand.brand_payback_max=request.POST['brand_payback_max']
            edit_brand.brand_floor_area_min=request.POST['brand_floor_area_min']
            edit_brand.brand_floor_area_max=request.POST['brand_floor_area_max']
            edit_brand.brand_payback_min_type=request.POST['brand_payback_min_type']
            edit_brand.brand_payback_max_type=request.POST['brand_payback_max_type']
            # print(request.POST['show_on_hp'])
            if request.POST['show_on_hp']=='Yes':
                # print('yes')
                show_on_hp=1
            else:
                show_on_hp=0
            edit_brand.brand_show_on_homepage=show_on_hp

            if 'brand_logo' in request.FILES.keys():
                # print(request.FILES['brand_logo'])
                image1=request.FILES['brand_logo'].read()
                path1="media/images/brand/"+str(request.FILES['brand_logo']).replace(' ','_')
                
                
                f=open(path1,'wb+')
                f.write(image1)
                f.close()
                
                url1=upload_file(path1,'franchise-brigade',"media/brand_image/"+str(request.POST['brand_name'])+".jpg")
                os.remove(path1)
            else:
                url1=edit_brand.brand_logo
                
            edit_brand.brand_logo=url1
            edit_brand.save()
            clearRedisCache()
            context['msg']="Brand Data Update Successfully"
            return render(request,'admin-panel/update-non-exclusive-brand.html', context)
        # return render(request,'admin-panel/update-brand.html',context)
    else:
        return un_authorized_access_handler(request)
# @login_required(login_url='/admin_login/')
@check_authentication
def delete_non_exclusive_brand(request):
    if check_authorization(request, permission_key='category_brand_mngt'):
        brand_id=request.GET['id']
        try:
            NonExclusiveBrands.objects.filter(id=brand_id).delete()
            clearRedisCache()
            return redirect("admin")
        except:
            return redirect("update_non_exclusive_brand", brand_id)
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')

@check_authentication
def add_brand(request):
    if check_authorization(request, permission_key='category_brand_mngt'):
        view_category=category.objects.all()
        context={'view_category':view_category}
        
        if request.method == 'GET':
            return render(request,'admin-panel/add-brand.html',context)

        if request.method=="POST":
            data={}

            user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id']) 

            fields=BrandSerializer().data.keys()
            
            for field in fields:
                try:
                    if field in request.POST:
                        if request.POST[field] not in emptyValuesList:
                            data[field]=request.POST[field]
                except Exception as e:
                    print('ERROR:\nfile_name',__file__+'\nerror:'+str(e)+'\n')

            for i in request.POST.getlist('brand_royalty_type[]'):
                print(i)
            data['brand_royalty_type']=json.dumps(request.POST.getlist('brand_royalty_type[]'))
            for i in request.POST.getlist('brand_royalty_fee[]'):
                print(i)
            data['brand_royalty_fee']=json.dumps(request.POST.getlist('brand_royalty_fee[]'))

            # MASTER FRANCHAISE
            data['brand_ismasterfranchaise']=request.POST['brand_ismasterfranchaise']
            if data['brand_ismasterfranchaise'] == 'no': 
                data['brand_master_investment_min']=0
                data['brand_master_investment_max']=0
                
            gallery=[]
            if 'brand_gallery[]' in request.FILES.keys() :
                # print(request.FILES.getlist('brand_gallery[]'))
                for p in request.FILES.getlist('brand_gallery[]'):
                    # print(p)
                    path="media/images/brand/"+str(p).replace(' ','_')
                    image=p.read()
                    f=open(path,'wb+')
                    f.write(image)
                    f.close()
                    url=upload_file(path,'franchise-brigade',"media/brand_image/"+str(request.POST['brand_name']).replace(' ','_')+'_'+str(i)+".jpg")
                    # os.remove(path)
                    gallery.append(url)
                    i=int(i)+1
                # print(gallery)
                
            if 'brand_logo' in request.FILES.keys():
                image1=request.FILES['brand_logo'].read()
                path1="media/images/brand/"+str(request.FILES['brand_logo']).replace(' ','_')
                f=open(path1,'wb+')
                f.write(image1)
                f.close()
                url1=upload_file(path1,'franchise-brigade',"media/brand_image/"+str(request.POST['brand_name']).replace(' ','_')+"_logo.jpg")
                # os.remove(path1)
            else:
                url1=""
            data['brand_logo']=url1
            data['brand_gallery']=json.dumps(gallery)
            data['category_id']=category.objects.get(id=data['category_id'])
            data['brand_slug']=getslug(data['brand_name'])

            logs=[{ "action_type":"insert", "requested_by":user_data['firstname']+' '+user_data['lastname'], "requested_user_id":user_data['id'],"requested_at":str(timezone.now())}]

            if is_admin(request):
                msg='Brand Data Added Successfuly'
                logs[0].update({"response_by":user_data['firstname']+' '+user_data['lastname'], "response_user_id":user_data['id'], "responsed_at":str(timezone.now()),"update_data":[]})
                data['logs']=json.dumps(logs)
                brand.objects.create(**data)
                clearRedisCache()
            else:
                msg='A request has been sent to Admin'
                logs[0].update({"response_by":"", "response_user_id":"", "responsed_at":"","update_data":[]})                
                data['logs']=json.dumps(logs)
                data['actor']=user_data['id']
                tc=Temp_Brand.objects.create(**data)
                push_notification(From=user_data['id'],from_role='employee',to=get_admin_ids(),to_role='admin',
                            title=f"Brand -  insert request by {user_data['firstname']}", url=f"/approval-requests?for=brand&id={tc.id}" )
            return render(request, 'admin-panel/alert.html',{'msg':msg,'redirect_location':'/add_brand'})
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def add_non_exclusive_brand(request):
    if check_authorization(request, permission_key='category_brand_mngt'):
        view_category=category.objects.all()
        context={'view_category':view_category}

        if request.method == 'GET':
            return render(request, 'admin-panel/add-non-exclusive-brand.html', context)

        if request.method == 'POST':
            if 'brand_logo' in request.FILES.keys():
                image1=request.FILES['brand_logo'].read()
                path1="media/images/brand/"+str(request.FILES['brand_logo']).replace(' ','_')
                f=open(path1,'wb+')
                f.write(image1)
                f.close()
                url1=upload_file(path1,'franchise-brigade',"media/brand_image/"+str(request.POST['brand_name'])+".jpg")
                # os.remove(path1)
            else:
                url1=""
            brand_logo=url1
            # brand_gallery=url
            if request.POST['show_on_hp']=="Yes":
                show_on_hp="1"
            else:
                show_on_hp="0"
            non_excl_obj=NonExclusiveBrands.objects.create(
                    id=uuid.uuid4(),
                    brand_name=request.POST['brand_name'],
                    brand_slug=getslug(request.POST['brand_name']),
                    category_id=request.POST['category_id'],
                    brand_logo=brand_logo,
                    brand_outlets=request.POST['brand_outlets'],
                    yr_of_establish=request.POST['brand_since'],
                    brand_inv_min=request.POST['brand_inv_min'],
                    brand_inv_min_type=request.POST['brand_inv_min_type'],
                    brand_inv_max=request.POST['brand_inv_max'],
                    brand_inv_max_type=request.POST['brand_inv_max_type'],
                    brand_payback_min=request.POST['brand_payback_min'],
                    brand_payback_max=request.POST['brand_payback_max'],
                    brand_floor_area_min=request.POST['brand_floor_area_min'],
                    brand_floor_area_max=request.POST['brand_floor_area_max'],
                    brand_payback_min_type=request.POST['brand_payback_min_type'],
                    brand_payback_max_type=request.POST['brand_payback_max_type'],
                    brand_show_on_homepage=show_on_hp
            )
            clearRedisCache()
            context['msg']="Brand Added Successfully"
            return render(request, 'admin-panel/add-non-exclusive-brand.html', context)
    else:
        return un_authorized_access_handler(request)


@check_authentication
def neb_bulk_upload(request):
    if request.method == 'GET':
        file_path=str(settings.BASE_DIR)+"/files/"+'non_exclusive_brand_bulk_upload.xlsx'
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = 'attachment; filename="non_exclusive_brand_bulk_upload.xlsx"'
        return response
    if request.method == 'POST':
        return render(request, 'admin-panel/alert.html',{'msg':"This feature is currently in Development Phase",'redirect_location':'/add-non-exclusive-brand/'})
        if 'file' not in request.FILES:
            return render(request, 'admin-panel/alert.html',{'msg':"Please Select File",'redirect_location':'/add-non-exclusive-brand/'})
        if os.path.splitext(request.FILES["file"].name)[1].lower() not in ['.xlsx']:
            return render(request, 'admin-panel/alert.html',{'msg':"Please Select file with .xlsx extension",'redirect_location':'/add-non-exclusive-brand/'})
        with open (str(settings.BASE_DIR)+"/temp_files/"+request.FILES["file"].name, 'wb+') as file_obj:
            for chunk in request.FILES["file"].chunks():
                file_obj.write(chunk)
        file_obj.close()
        filehandler=NonExclusinveBulkUPload(file_obj.name)
        msg=filehandler.insert_neb()
        return render(request, 'admin-panel/alert.html',{'msg':msg,'redirect_location':'/add-non-exclusive-brand/'})
        # pass

# _________________________________________________ Client Data Management __________________________________________________________

@check_authentication
def list_ur_brand_data(request):
    if check_authorization(request, permission_key='client_data_mngt'):
        user_brand_data=list_ur_brand.objects.all().order_by('-submition_date')
        invester_data=invester_details.objects.all().order_by('-submition_date')
        context={'user_data':user_brand_data,'invester_data':invester_data,}
        return render(request,'admin-panel/registration-form.html',context)
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def single_brand_ur_list(request,pk):
    if check_authorization(request, permission_key='client_data_mngt'):
        user_brand_data=list_ur_brand.objects.get(pk=pk)       
        context={'user_data':user_brand_data}
        return render(request,'admin-panel/brand-registration-form-details.html',context)  
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def single_invester_list(request,pk): 
    if check_authorization(request, permission_key='client_data_mngt'):   
        invester_data=invester_details.objects.get(pk=pk)
        context={'invester_data':invester_data}
        return render(request,'admin-panel/invester-registration-form-details.html',context)  
    else:
        return un_authorized_access_handler(request)


# @login_required(login_url='/admin_login/')
@check_authentication
def contact_us_data(request):
    if check_authorization(request, permission_key='client_data_mngt'):
        contact_data=contactus.objects.all().order_by('-id')    
        newsletters_data=newsletters.objects.all().order_by('-id')  
        cat_inquery_form_data=cat_inquery.objects.all().order_by('-id')    
        brand_inquery_form_data=brand_inquery.objects.all().order_by('-id')  
        consultasy_form_data=consultancy.objects.all().order_by('-id')  
        directory_inquiry=dir_inquery.objects.all().order_by('-id')
        
        for item in directory_inquiry:
            temp_category=category.objects.filter(id=item.category_id).get()
            temp_brand=""
            # print(item.brand_type)
            if item.brand_type=="eb":
                try:
                    temp_brand=brand.objects.filter(id=item.brand_id).get()
                except brand.DoesNotExist:
                    item.delete()
                    continue
            else:
                try:
                    temp_brand=NonExclusiveBrands.objects.filter(id=item.brand_id).get()
                    # print(temp_brand)
                except NonExclusiveBrands.DoesNotExist:
                    item.delete()
                    continue

            setattr(item, 'brand', temp_brand)
            setattr(item, 'category', temp_category)
        context={
            'user_data':contact_data,
            'cat_inquery_form_data':cat_inquery_form_data, 
            'brand_inquery_form_data':brand_inquery_form_data,   
            'consultasy_form_data':consultasy_form_data, 
            'newsletters_data':newsletters_data,
            'directory_inquiry':directory_inquiry,
        }
        return render(request,'admin-panel/contact-form.html',context)
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def cat_inquery_form_data(request,ck):
    if check_authorization(request, permission_key='client_data_mngt'):
        cat_inquery_form_data=cat_inquery.objects.get(pk=ck)       
        context={'category_inq_data':cat_inquery_form_data}   
        return render(request,'admin-panel/category-and-industry-details-form.html',context) 
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def brand_inquery_form_data(request,bk):
    if check_authorization(request, permission_key='client_data_mngt'):   
        brand_inquery_form_data=brand_inquery.objects.get(pk=bk)         
        context={'cat_inquery_form_data':cat_inquery_form_data, 'brand_inq_data':brand_inquery_form_data}   
        return render(request,'admin-panel/brand-and-industry-details-form.html',context) 
    else:
        return un_authorized_access_handler(request)


@check_authentication
def contact_us_single_data(request,pk):
    if check_authorization(request, permission_key='client_data_mngt'):
        contact_data=contactus.objects.get(pk=pk)    
        context={'user_data':contact_data}
        return render(request,'admin-panel/contact-us-form-details.html',context) 
    else:
        return un_authorized_access_handler(request)


@check_authentication
def export_form_data_view(request):
    if check_authorization(request, permission_key='client_data_mngt'):
        if request.method=="GET":
            return render(request, 'admin-panel/export.html')

        if request.method=="POST":
            fromdate=None
            todate=None
            formname=request.POST['formname']
            if not formname in formnames.keys():
                return HttpResponse("Invalidresponse")
            if request.POST['selectMonth']=='custom':
                if 'from' in request.POST and request.POST['from']!='':
                    fromdate=request.POST['from']
                if 'to' in request.POST and request.POST['to']!='':
                    todate=request.POST['to']
            else:
                fromdate=str(date.today()+timedelta(days=-30*int(request.POST['selectMonth'])))
            # filename=export_form_to_excel(fromdate=fromdate, todate=todate)
            # return FileResponse(open(filename, 'rb'), as_attachment=True)
            response=export_form_to_excel(formname=formname,fromdate=fromdate, todate=todate)
            return response
    else:
        return un_authorized_access_handler(request)



# @login_required(login_url='/admin_login/')
# def consultasy_form_data(request,bk):
   
#     brand_inquery_form_data=brand_inquery.objects.get(pk=bk)      
#     view_category=category.objects.all()
#     home_details=Home_Details.objects.get()   
#     context={
#         'view_category':view_category,
#         'home_details':home_details,
#         # 'user_data':contact_data,
#         'cat_inquery_form_data':cat_inquery_form_data, 
#         'brand_inq_data':brand_inquery_form_data,    
        
#     }   
#     return render(request,'admin-panel/brand-and-industry-details-form.html',context) 



# ________________________________________________ Site BOTs management _________________________________________________________

@check_authentication
def add_bot(request):
    if check_authorization(request, permission_key='bots_mngt'):
        context={'pages':pages}

        if request.method == "GET":
            return render(request, 'admin-panel/add-script.html', context)
        
        if request.method == "POST":   
            bot_pages=request.POST.getlist('bot_pages[]')
            if 'all' in bot_pages:
                bot_pages='all'
            else:
                bot_pages=';'.join(bot_pages)
            # return render(request, 'admin-panel/alert.html',{'msg':'Bot Added Successfuly',' redirect_location':'/add-bot'})
            """
                POSITION : head -- > 1
                        : body -- > 2
            """
            if request.POST['bot_position'] == 'head':
                position=1
            else:
                position=2

            bot_obj=Site_Bots(
                bot_name=request.POST['bot_name'],
                bot_slug=getslug(request.POST['bot_name']),
                bot_script=request.POST['bot_script'],
                bot_position=position,
                is_bot_active=request.POST['is_bot_active'],
                bot_display_on=bot_pages
            )
            bot_obj.save()
            clearRedisCache()
            return render(request, 'admin-panel/alert.html',{'msg':'Bot Added Successfuly',' redirect_location':'/add-bot'})
    else:
        return un_authorized_access_handler(request)


# @login_required(login_url='/admin_login/')
@check_authentication
def delete_bot(request):
    if check_authorization(request, permission_key='bots_mngt'):
        try:
            botslug=request.GET['id']
            thisbot=Site_Bots.objects.filter(bot_slug=botslug).get()
            thisbot.delete()
            clearRedisCache()
            return render(request, 'admin-panel/alert.html',{'msg':'Bot Data Deleted Successfuly','redirect_location':'/admin'})
        except:
            return redirect("/update-bot/none")
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def update_bot(request, botslug):
    context={}
    if check_authorization(request, permission_key='bots_mngt'):
        if botslug =='none':
            context['bots']=Site_Bots.objects.all()
            return render(request, 'admin-panel/update-script.html', context)
        try:
            thisbot=Site_Bots.objects.filter(bot_slug=botslug).get()
        except Site_Bots.DoesNotExist:
            pass
            return redirect("/admin/")
        context['thisbot']=thisbot
        context['pages']=pages
        context['bot_pages']=thisbot.bot_display_on.split(';')

        if request.method == "GET":
            return render(request, 'admin-panel/update-script.html', context)
        
        if request.method == "POST": 
            
            if request.POST['bot_position'] == 'head':
                thisbot.bot_position=1
            else:
                thisbot.bot_position=2
            
            bot_pages=request.POST.getlist('bot_pages[]')
            if 'all' in bot_pages:
                bot_pages='all'
            else:
                bot_pages=';'.join(bot_pages)
            
            thisbot.bot_display_on=bot_pages
            thisbot.bot_name=request.POST['bot_name']
            thisbot.bot_script=request.POST['bot_script']
            thisbot.is_bot_active=request.POST['is_bot_active']
            thisbot.save()
            clearRedisCache()
            return render(request, 'admin-panel/alert.html',{'msg':'Bot Data Updated Successfuly',' redirect_location':f'/update-bot/{thisbot.bot_slug}'})
    else:
        return un_authorized_access_handler(request)


# __________________________________________________ User Access Management _________________________________________________________

@check_authentication
def add_employee(request):
    if check_authorization(request, permission_key='uam'):
        context={'all_permissions':employee_access}
        if request.method == 'GET':
            return render(request, 'admin-panel/create-user.html', context)
        if request.method == 'POST':
            try:
                user_access=request.POST.getlist('access[]')
                user_access=';'.join(user_access)

                enctypted_password=pbkdf2_sha256.hash('1234567890',rounds=1200,salt_size=32)    
                user_obj=Employee(
                    firstname   =   request.POST['firstname'],
                    lastname    =   request.POST['lastname'],
                    email       =   request.POST['email'].lower(),
                    password    =   enctypted_password,
                    access      =   user_access
                )
                user_obj.save()
                login_url=settings.DOMAIN_ADDRS+'/admin_login/'
                send_mail("Franchise Brigade:Welcome",f'Welcom to Franchise Brigade<br> <a href="{login_url}"> click here</a> to login.',settings.EMAIL_HOST_USER,[user_obj.email],fail_silently=False)
                return render(request, 'admin-panel/alert.html',{'msg':'User Added Successfuly',' redirect_location':'/add-employee'})
            except Exception as e:
                return render(request, 'admin-panel/alert.html',{'msg':f'Error:{str(e)}',' redirect_location':'/add-employee'})
    else:
        return un_authorized_access_handler(request)

# @login_required(login_url='/admin_login/')
@check_authentication
def update_employee(request, userid):
    if check_authorization(request, permission_key='uam'):
        context={}
        if userid == 0 or userid == '0':
            context['users']=Employee.objects.all()
            return render(request, 'admin-panel/update-users.html', context)
        else:
            if request.method == 'GET':
                try:
                    context['thisuser']=Employee.objects.get(id=userid)
                    context['user_permissions']=context['thisuser'].access.split(';')
                    context['all_permissions']=employee_access
                    return render(request, 'admin-panel/update-user.html', context)
                except Employee.DoesNotExist:
                    return render(request, 'admin-panel/alert.html',{'msg':'This User Data Not exists','redirect_location':'/update-employee/0'})

            if request.method == 'POST':
                try:
                    user_obj=Employee.objects.get(id=userid)
                    user_access=request.POST.getlist('access[]')
                    user_access=';'.join(user_access)
                    user_obj.firstname   =   request.POST['firstname']
                    user_obj.lastname    =   request.POST['lastname']
                    user_obj.email       =   request.POST['email'].lower()
                    user_obj.access      =   user_access
                    user_obj.is_active   =   request.POST['is_active']
                    user_obj.save()
                    return render(request, 'admin-panel/alert.html',{'msg':'User Data Updated Successfuly','redirect_location':'/update-employee/0'})
                except Employee.DoesNotExist:
                    return render(request, 'admin-panel/alert.html',{'msg':'This User Data Not exists','redirect_location':'/update-employee/0'})
                except Exception as e:
                    return render(request, 'admin-panel/alert.html',{'msg':f'Error:{str(e)}',' redirect_location':'/update-employee/0'})
    else:
        return un_authorized_access_handler(request)


@check_authentication
def delete_employee(request, userid):
    if check_authorization(request, permission_key='uam'):
        try:
            user_obj=Employee.objects.get(id=userid)
            user_obj.delete()
            return redirect('/update-employee/0')
        except Employee.DoesNotExist:
            return render(request, 'admin-panel/alert.html',{'msg':'This User Data Not exists','redirect_location':'/update-employee/0'})
    else:
        return un_authorized_access_handler(request)

# ___________________________________________________ Notifications ______________________________________________________

@check_authentication
def show_all_notification(request):
    user_data=get_logged_user_data(request, ['id'])
    all_notifications=Notifications.objects.filter(notification_to=user_data['id']).order_by('-created_at').all()
    context={'notifications':all_notifications}
    return render(request,'admin-panel/notifications.html',context)


# ________________________________________________________  Approval Requests _____________________________________________________
@check_authentication
def approval_requests(request):
    # Check authorization
    if is_admin(request):
        # required data collection
        url_data=request.GET.dict()
        For=action=id=notification_id=None
        context={'emptyvalues':emptyValuesList}
        if 'for' in url_data:
            For=url_data['for']
        if 'action' in url_data:
            action=url_data['action']
        if 'id' in url_data:
            id=url_data['id']

        if 'notification' in url_data:
            update_notification_status(request)
        
        redirect_url='/approval-requests?for=none&id=none' if 'next' not in request.GET else request.GET['next']

        if (For in ['none','',None]) or ('id' in ['none','',None]):
            context['category_requests']=Temp_Category.objects.all()
            context['brand_requests']=Temp_Brand.objects.all()
            context['blog_requests']=Temp_Blog.objects.all()
            return render(request, 'admin-panel/approval-requests.html', context)

        if For=='category':
            if action in [None, '', ' ']:
                try:
                    context['req']=Temp_Category.objects.get(id=id)
                    context['emp']=Employee.objects.get(id=context['req'].actor)
                    if context['req'].task_type in ['delete', 'update']:
                        context['current_data']=category.objects.get(id=context['req'].to_category_id)
                    return render(request, 'admin-panel/approval-request-action.html', context)
                except Temp_Category.DoesNotExist:
                    return send_alert_msg(request,'You or Someone has already took an action',redirect_url)
                except:
                    return send_alert_msg(request,'Internal Server Error',redirect_url)
            else:
                return admin_action_on_category_request(request,id,action)
       
        elif For=='brand':
            if action in [None, '', ' ']:
                try:
                    context['req']=Temp_Brand.objects.get(id=id)
                    context['emp']=Employee.objects.get(id=context['req'].actor)
                    # royalty=[]
                    # royalty_type=json.loads(context['req'].brand_royalty_type)
                    # royalty_fee=json.loads(context['req'].brand_royalty_fee)
                    # for i in range(0,len(json.loads(context['req'].brand_royalty_type))):
                        # royalty.append({'royalty_type':royalty_type[i],'royalty_fee': royalty_fee[i]})
                    if context['req'].task_type=='insert':
                        context['req_royalty']=get_brand_royalty(context['req'])
                        context['req_gallery']=json.loads(context['req'].brand_gallery)
                    if context['req'].task_type in ['delete', 'update']:
                        context['current_data']=brand.objects.get(id=context['req'].to_brand_id)
                        context['current_data_royalty']=get_brand_royalty(context['current_data'])
                        print(context['current_data_royalty'])
                        context['current_data_gallery']=json.loads(context['current_data'].brand_gallery)
                    return render(request, 'admin-panel/approval-request-action.html', context)
                except Temp_Brand.DoesNotExist:
                    return send_alert_msg(request,'You or Someone has already took an action',redirect_url)
                except:
                    return send_alert_msg(request,'Internal Server Error',redirect_url)
            else:
                return admin_action_on_brand_request(request,id,action)
       
        elif For=='blog':
            if action in [None, '', ' ']:
                try:
                    context['req']=Temp_Blog.objects.get(id=id)
                    context['emp']=Employee.objects.get(id=context['req'].actor)
                    if context['req'].task_type in ['delete','update']:
                        context['current_data']=blog.objects.get(id=context['req'].to_blog_id)
                    return render(request, 'admin-panel/approval-request-action.html', context)
                except Temp_Blog.DoesNotExist:
                    return send_alert_msg(request,'You or Someone has already took an action',redirect_url)
                except Exception as e:
                    return send_alert_msg(request,'Internal Server Error',redirect_url)
            else:
                return admin_action_on_blog_request(request,id,action)

        return HttpResponse('Hi Man')

    else:
        return un_authorized_access_handler(request)




def admin_action_on_category_request(request, req_id, action):
    # Initial verification 
    try:
        temp_cat_obj=Temp_Category.objects.get(id=req_id)
    except Temp_Category.DoesNotExist:
        return send_alert_msg(request,'You or Someone has already took an action','/approval-requests?for=none&id=none')
    except:
        return send_alert_msg(request,'Internal Server Error','/approval-requests?for=none&id=none')
    if action in [None,'', ' ']:
        return HttpResponse('GET request')
    
    # Loading required data
    user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id'])
    notification_title=''
    notification_url='/admin/'

    # Logs updataion
    logs=json.loads(temp_cat_obj.logs)
    last_log=logs[len(logs)-1]
    last_log["response_by"]=user_data['firstname']+' '+user_data['lastname']
    last_log["response_user_id"]=user_data['id']  
    last_log["responsed_at"]=str(timezone.now())
    last_log['action']=action

    # If category insert request
    if temp_cat_obj.task_type=='insert':
        if action=='approve':
            data={}
            # Collecting category request data and storing in 'data' dictionary
            for field in CategorySerializer().data.keys():
                try:
                    data[field]=temp_cat_obj.__getattribute__(field)
                except:
                    pass
            # Category data insertion
            cat_obj=category.objects.create(**data)
            cat_obj.logs=json.dumps(logs)
            cat_obj.save()
            #setting notification data
            notification_url=f"/update_category/{cat_obj.id}"
            notification_title=f"Category - insert approved by {user_data['firstname']}"
            response=send_alert_msg(request,'Category Insertion Request Approved','/approval-requests?for=none&id=none')
        
        elif action=='reject':
            # If this is the case only need to remove the temp_category data from the database. and send the notification back to the user who requested
            notification_title=f"Category - insert rejected by {user_data['firstname']}"
            response=send_alert_msg(request,'Category Insertion Request Rejected','/approval-requests?for=none&id=none')
        
        else:
            return send_alert_msg(request,'Invalid Request','/approval-requests?for=none&id=none')

    # If category delete request
    elif temp_cat_obj.task_type =='delete':
        if action=='approve':
            cat=category.objects.get(id=temp_cat_obj.to_category_id)
            try:
                # delete all brands , non exclusive brands under this category, delete the category
                # logs=[{ "action_type":"delete", "requested_by":user_data['firstname']+' '+user_data['lastname'], "requested_user_id":user_data['id'],"requested_at":str(timezone.now())}]       
                brands=brand.objects.filter(category_id=cat).all()
                nebs=NonExclusiveBrands.objects.filter(category_id=cat.id).all()
                
                for b in brands:
                    move_this_record_to_bin(b.id,b.brand_name,'brand',BrandSerializer(b).data)
                for neb in nebs:
                    move_this_record_to_bin(neb.id,neb.brand_name,'non_exclusive_brand',NonExclusiveBrandSerializer(neb).data)
                
                move_this_record_to_bin(cat.id,cat.category_name,'category',CategorySerializer(cat).data)
                
                brands.delete()
                nebs.delete()
                # cat.logs=json.loads()
                cat.delete()
                # setting notification title, and response
                notification_title=f"Category - delete approved by {user_data['firstname']}"
                response=send_alert_msg(request,'Category Deletetion Request Approved','/approval-requests?for=none&id=none')
            except:
                response=send_alert_msg(request,'Internal Error','/approval-requests?for=none&id=none')

        elif action=='reject':
            # Update log data
            cat=category.objects.get(id=temp_cat_obj.to_category_id)
            current_logs=json.loads(cat.logs)
            current_logs.append(last_log)
            cat.logs=json.dumps(current_logs)
            cat.save()
            # Set notification title
            notification_title=f"Category - delete rejected by {user_data['firstname']}"
            response=send_alert_msg(request,'Category Deletetion Request Rejected','/approval-requests?for=none&id=none')
        else:
            return send_alert_msg(request,'Invalid Request','/approval-requests?for=none&id=none')
    
    # If category update request
    elif temp_cat_obj.task_type =='update':
        if action=='approve':
            data={}
            model_fields=CategorySerializer().data.keys()
            temp_model_fields=TempCategorySerializer().data.keys()

            for field in model_fields:
                try:
                    if field in temp_model_fields:
                        value=temp_cat_obj.__getattribute__(field)
                        if  value not  in [ '#','',' ']:
                            data[field]=value
                except:
                    pass
            category.objects.filter(id=temp_cat_obj.to_category_id).update(**data)
            cat_obj=category.objects.get(id=temp_cat_obj.to_category_id)
            # logs updatation
            current_logs=json.loads(cat_obj.logs)
            current_logs.append(last_log)
            cat_obj.logs=json.dumps(current_logs)
            cat_obj.save()
            # notification_url=f"/admin/"
            notification_title=f"Category - update approved by {user_data['firstname']}"
            response=send_alert_msg(request,'Category Updation Request Approved','/approval-requests?for=none&id=none')

        elif action=='reject':
            cat_obj=category.objects.get(id=temp_cat_obj.to_category_id)
            current_logs=json.loads(cat_obj.logs)
            current_logs.append(last_log)
            cat_obj.logs=json.dumps(current_logs)
            cat_obj.save()
            notification_title=f"Category - update rejected by{user_data['firstname']}"
            response=send_alert_msg(request,'Category Updation Request Rejected','/approval-requests?for=none&id=none')

        else:
            return send_alert_msg(request,'Invalid Request','/approval-requests?for=none&id=none')

    else:
        return redirect('/approval-requests')
    
    temp_cat_obj.delete()
    update_notification_status(request)
    push_notification(From=user_data['id'],from_role='admin',to=[temp_cat_obj.actor],to_role='employee',
            title=notification_title, url=notification_url)
    clearRedisCache()
    return response



def admin_action_on_brand_request(request,req_id,action):
    # Initial verification 
    try:
        temp_brand_obj=Temp_Brand.objects.get(id=req_id)
    except Temp_Brand.DoesNotExist:
        return send_alert_msg(request,'You or Someone has already took an action','/approval-requests?for=none&id=none')
    except:
        return send_alert_msg(request,'Internal Server Error','/approval-requests?for=none&id=none')
    
    # Loading required data
    user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id'])
    notification_title=''
    notification_url='/admin/'

    # Logs updataion
    # logs=json.loads(temp_brand_obj.logs)
    # last_log=logs[len(logs)-1]
    # last_log["response_by"]=user_data['firstname']+' '+user_data['lastname']
    # last_log["response_user_id"]=user_data['id']  
    # last_log["responsed_at"]=str(timezone.now())
    # last_log['action']=action

    # If category insert request
    if temp_brand_obj.task_type=='insert':
        if action=='approve':
            data={}
            # Collecting category request data and storing in 'data' dictionary
            for field in BrandSerializer().data.keys():
                try:
                    data[field]=temp_brand_obj.__getattribute__(field)
                except:
                    pass
            # Category data insertion
            brand_obj=brand.objects.create(**data)
            # brand_obj.logs=json.dumps(logs)
            brand_obj.save()
            #setting notification data
            notification_url=f"/update_brand/{brand_obj.id}"
            notification_title=f"Brand - insert approved by {user_data['firstname']}"
            response=send_alert_msg(request,'Brand Insertion Request Approved','/approval-requests?for=none&id=none')
        
        elif action=='reject':
            # If this is the case only need to remove the temp_category data from the database. and send the notification back to the user who requested
            notification_title=f"Brand - insert rejected by {user_data['firstname']}"
            response=send_alert_msg(request,'Brand Insertion Request Rejected','/approval-requests?for=none&id=none')
        
        else:
            return send_alert_msg(request,'Invalid Request','/approval-requests?for=none&id=none')

    # If category delete request
    elif temp_brand_obj.task_type =='delete':
        if action=='approve':
            bd=brand.objects.get(id=temp_brand_obj.to_brand_id)
            try:
                move_this_record_to_bin(bd.id,bd.brand_name,'brand',BrandSerializer(bd).data,logs=None)
                bd.delete()
                # setting notification title, and response
                notification_title=f"Brand - delete approved by {user_data['firstname']}"
                response=send_alert_msg(request,'Brand Deletetion Request Approved','/approval-requests?for=none&id=none')
            except:
                response=send_alert_msg(request,'Internal Error','/approval-requests?for=none&id=none')

        elif action=='reject':
            # Update log data
            bd=brand.objects.get(id=temp_brand_obj.to_brand_id)
            # current_logs=json.loads(bd.logs)
            # current_logs.append(last_log)
            # bd.logs=json.dumps(current_logs)
            bd.save()
            # Set notification title
            notification_title=f"Brand - delete rejected by {user_data['firstname']}"
            response=send_alert_msg(request,'Brand Deletetion Request Rejected','/approval-requests?for=none&id=none')
        else:
            return send_alert_msg(request,'Invalid Request','/approval-requests?for=none&id=none')
    
    # If category update request
    elif temp_brand_obj.task_type =='update':
        if action=='approve':
            data={}
            model_fields=BrandSerializer().data.keys()
            temp_model_fields=TempBrandSerializer().data.keys()

            for field in model_fields:
                try:
                    if field in temp_model_fields:
                        value=temp_brand_obj.__getattribute__(field)
                        if  value not  in emptyValuesList:
                            data[field]=value
                except:
                    pass
            brand.objects.filter(id=temp_brand_obj.to_brand_id).update(**data)
            brand_obj=brand.objects.get(id=temp_brand_obj.to_brand_id)
            # logs updatation
            # current_logs=json.loads(brand_obj.logs)
            # current_logs.append(last_log)
            # brand_obj.logs=json.dumps(current_logs)
            brand_obj.save()
            # notification_url=f"/admin/"
            notification_title=f"Brand - update approved by {user_data['firstname']}"
            response=send_alert_msg(request,'Brand Updation Request Approved','/approval-requests?for=none&id=none')

        elif action=='reject':
            brand_obj=brand.objects.get(id=temp_brand_obj.to_brand_id)
            # current_logs=json.loads(brand_obj.logs)
            # current_logs.append(last_log)
            # brand_obj.logs=json.dumps(current_logs)
            brand_obj.save()
            notification_title=f"Brand - update rejected by {user_data['firstname']}"
            response=send_alert_msg(request,'Brand Updation Request Rejected','/approval-requests?for=none&id=none')

        else:
            return send_alert_msg(request,'Invalid Request','/approval-requests?for=none&id=none')

    else:
        return redirect('/approval-requests')
    
    temp_brand_obj.delete()
    update_notification_status(request)
    push_notification(From=user_data['id'],from_role='admin',to=[temp_brand_obj.actor],to_role='employee',
            title=notification_title, url=notification_url)
    clearRedisCache()
    return response


def admin_action_on_blog_request(request,req_id,action):
    # Initial verification 
    try:
        temp_blog_obj=Temp_Blog.objects.get(id=req_id)
    except Temp_Blog.DoesNotExist:
        return send_alert_msg(request,'You or Someone has already took an action','/approval-requests?for=none&id=none')
    except:
        return send_alert_msg(request,'Internal Server Error','/approval-requests?for=none&id=none')
    
    # if action in [None,'', ' ']:
    #     return HttpResponse('GET request')
    
    # Loading required data
    user_data=get_logged_user_data(request, ['firstname', 'lastname', 'id'])
    notification_title=''
    notification_url='/admin/'

    # Logs updataion
    # logs=json.loads(temp_blog_obj.logs)
    # last_log=logs[len(logs)-1]
    # last_log["response_by"]=user_data['firstname']+' '+user_data['lastname']
    # last_log["response_user_id"]=user_data['id']  
    # last_log["responsed_at"]=str(timezone.now())
    # last_log['action']=action

    # If blog insert request
    if temp_blog_obj.task_type=='insert':
        if action=='approve':
            data={}
            for field in BlogSerializer().data.keys():
                try:
                    data[field]=temp_blog_obj.__getattribute__(field)
                except:
                    pass
            # Category data insertion
            blog_obj=blog.objects.create(**data)
            # brand_obj.logs=json.dumps(logs)
            # brand_obj.save()
            #setting notification data
            notification_url=f"/update-single-blog/{blog_obj.id}"
            notification_title=f"Blog - insert approved by {user_data['firstname']}"
            response=send_alert_msg(request,'Blog Insertion Request Approved','/approval-requests?for=none&id=none')
        elif action=='reject':
            # If this is the case only need to remove the temp_category data from the database. and send the notification back to the user who requested
            notification_title=f"Blog - insert rejected by {user_data['firstname']}"
            response=send_alert_msg(request,'Blog Insertion Request Rejected','/approval-requests?for=none&id=none')
        else:
            return send_alert_msg(request,'Invalid Request','/approval-requests?for=none&id=none')

    # If category delete request
    elif temp_blog_obj.task_type =='delete':
        if action=='approve':
            blg=blog.objects.get(id=temp_blog_obj.to_blog_id)
            try:
                move_this_record_to_bin(blg.id,blg.blog_title,'blog',BlogSerializer(blg).data,logs=None)
                blg.delete()
                # setting notification title, and response
                notification_title=f"Blog - delete approved by {user_data['firstname']}"
                response=send_alert_msg(request,'Blog Deletetion Request Approved','/approval-requests?for=none&id=none')
            except:
                response=send_alert_msg(request,'Internal Error','/approval-requests?for=none&id=none')

        elif action=='reject':
            # Update log data
            # blg=blog.objects.get(id=temp_blog_obj.to_blog_id)
            # current_logs=json.loads(bd.logs)
            # current_logs.append(last_log)
            # bd.logs=json.dumps(current_logs)
            # bd.save()
            # Set notification title
            notification_title=f"Blog - delete rejected by {user_data['firstname']}"
            response=send_alert_msg(request,'Blog Deletetion Request Rejected','/approval-requests?for=none&id=none')
        else:
            return send_alert_msg(request,'Invalid Request','/approval-requests?for=none&id=none')
    
    # If category update request
    elif temp_blog_obj.task_type =='update':
        if action=='approve':
            data={}
            model_fields=BlogSerializer().data.keys()
            temp_model_fields=TempBlogSerializer().data.keys()

            for field in model_fields:
                try:
                    if field in temp_model_fields:
                        value=temp_blog_obj.__getattribute__(field)
                        if  value not  in emptyValuesList :
                            data[field]=value
                except:
                    pass
            blog.objects.filter(id=temp_blog_obj.to_blog_id).update(**data)
            # brand_obj=brand.objects.get(id=temp_brand_obj.to_brand_id)
            # logs updatation
            # current_logs=json.loads(brand_obj.logs)
            # current_logs.append(last_log)
            # brand_obj.logs=json.dumps(current_logs)
            # brand_obj.save()
            # notification_url=f"/admin/"
            notification_title=f"Blog - update approved by {user_data['firstname']}"
            response=send_alert_msg(request,'Blog Updation Request Approved','/approval-requests?for=none&id=none')

        elif action=='reject':
            # brand_obj=brand.objects.get(id=temp_brand_obj.to_brand_id)
            # current_logs=json.loads(brand_obj.logs)
            # current_logs.append(last_log)
            # brand_obj.logs=json.dumps(current_logs)
            # brand_obj.save()
            notification_title=f"Blog - update {user_data['firstname']}"
            response=send_alert_msg(request,'Blog Updation Request Rejected','/approval-requests?for=none&id=none')
        else:
            return send_alert_msg(request,'Invalid Request','/approval-requests?for=none&id=none')
    else:
        return redirect('/approval-requests')
    
    temp_blog_obj.delete()
    update_notification_status(request)
    push_notification(From=user_data['id'],from_role='admin',to=[temp_blog_obj.actor],to_role='employee',
            title=notification_title, url=notification_url)
    clearRedisCache()
    return response

#====================================================================================================================
#                                              SITE / WEBSITE VIEWS  
#====================================================================================================================
#@cache_page(CACHE_TTL)
#frontend function
def front_index(request):
    update_upcomming_event_status()
    # sp=scrapertool()
    # news=sp.scrape()
    latest_blog=None
    latest_article=None
    # home_details=Home_Details.objects.get()
    about_data=about_sec.objects.get()
    category_data=category.objects.all()
    # category_data=category.objects.all()
    brand_data1=brand.objects.all()
    brands=brand.objects.all() #only featured
    review_data=review.objects.all()
    # blogs=blog.objects.all().order_by('-post_date')
    blogsall=blog.objects.all().order_by('-post_date')
    articles=Articles.objects.all().order_by('-created_at')
    if articles[0].created_at > blogsall[0].post_date:
        latest_article=articles[0]
        articles=articles[1:]
    else:
        latest_blog=blogsall[0]
        blogsall=blogsall[1:]
        
    events=event.objects.all()
    social_data=social_link.objects.get()
    food_bev=[]
    exclusive_brands=brands.filter(brand_featured_type='Yes').order_by('category_id')
    exclusive_categories=list(category.objects.all())
    neb=NonExclusiveBrands.objects.filter(brand_show_on_homepage="1")
    for cat in exclusive_categories:
        count=0
        if exclusive_brands.filter(category_id=cat.id):
            count=1
            setattr(cat, 'count', count)
            continue

    headbots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=1).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='index')).all()
    bodybots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=2).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='index')).all()

    # NEWS fetch
    newfilepath=Path(__file__).resolve().parent.parent.parent
    # print('file path:',newfilepath)
    news=pd.read_csv(str(newfilepath)+'/news.csv') 
    news=news.to_numpy()    
    
    context={
        # 'home_details':home_details,
        'about_data':about_data,
        'category_data':category_data,
        'brands_food_filter':brands.filter(id=7),
        'brand_data1':brand_data1,
        'pre_event_data':events.filter(event_status='No'),
        'up_event_data':events.filter(event_status='Yes'),
        'top_bussiness':brands.filter(brand_bussiness_opr_type='Yes'),
        'featured_brand':brands.filter(brand_featured_type='Yes'),
        'latest_blog':latest_blog,
        'blogsall':blogsall,
        'social_data':social_data,
        'review_data':review_data,
        'food_bev':brands.filter(category_id=7),
        'exclusive_categories':exclusive_categories,
        'exclusive_brands':exclusive_brands,
        'non_exclusive_brands':neb,
        'news':news[1:],
        'latest_news':news[0],
        'head_bots':headbots,
        'body_bots':bodybots,
        'articles':articles,
        'latest_article':latest_article
    }  
    
    return render(request,'front-end/index.html',context)

#@cache_page(CACHE_TTL)
def front_about(request):
    # home_details=Home_Details.objects.get()
    about_data=about_sec.objects.get()
    social_data=social_link.objects.get()
    category_data=category.objects.all()

    headbots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=1).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='about_us')).all()
    bodybots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=2).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='about_us')).all()
    
    context={
        # 'home_details':home_details,
        'about_data':about_data,
        'social_data':social_data,
        'category_data':category_data,
        'head_bots':headbots,
        'body_bots':bodybots,
    }
    return render(request,'front-end/about-us.html',context)

#@cache_page(CACHE_TTL)
def front_privacy_policy(request):
    # home_details=Home_Details.objects.get()
    social_data=social_link.objects.get()
    # about_data=about_sec.objects.get()
    category_data=category.objects.all()
    headbots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=1).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='privacy_and_policy')).all()
    bodybots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=2).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='privacy_and_policy')).all()

    context={
        # 'home_details':home_details,
        'social_data':social_data,
        'category_data':category_data,
        'head_bots':headbots,
        'body_bots':bodybots,
    }
    # print(about_data.footer_content)
    return render(request,'front-end/privacy-policy.html',context)

#@cache_page(CACHE_TTL)
def front_term_condition(request):
    # home_details=Home_Details.objects.get()
    # about_data=about_sec.objects.get()
    social_data=social_link.objects.get()
    category_data=category.objects.all()
    headbots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=1).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='terms_and_condition')).all()
    bodybots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=2).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='terms_and_condition')).all()

    context={
        # 'home_details':home_details,
        'social_data':social_data,
        'category_data':category_data,
        'head_bots':headbots,
        'body_bots':bodybots,
    }
    # print(about_data.footer_content)
    return render(request,'front-end/terms-and-conditions.html',context)

#@cache_page(CACHE_TTL)
def front_refund_cancelletion(request):
    # home_details=Home_Details.objects.get()
    # about_data=about_sec.objects.get()
    social_data=social_link.objects.get()
    category_data=category.objects.all()
    
    headbots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=1).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='refund_and_cancellation')).all()
    bodybots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=2).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='refund_and_cancellation')).all()
    

    context={
        # 'home_details':home_details,
        'social_data':social_data,
        'category_data':category_data,
        'head_bots':headbots,
        'body_bots':bodybots,
    }
    # print(about_data.footer_content)
    return render(request,'front-end/refund-and-cancellation.html',context)

#@cache_page(CACHE_TTL)
def front_category(request,pk):
    # home_details=Home_Details.objects.get()
    category_data=category.objects.all()
    category_data1=category.objects.get(category_slug=pk)
    # brands=brand.objects.filter(brand_featured_type="Yes").all()
    brands=brand.objects.filter(brand_featured_type="Yes").all()
    blogs=blog.objects.all()
    blogssi=blog.objects.all().order_by('-id')[0:2]
    social_data=social_link.objects.get()
    neb=NonExclusiveBrands.objects.filter(category_id=category_data1.id)
    
    headbots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=1).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='category_page')).all()
    bodybots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=2).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='category_page')).all()
    
    context={
        # 'home_details':home_details,
        'category_data':category_data,
        'category_data1':category_data1,
        'brands':brands.filter(category_id=category_data1.id),
        'top_bussiness':brands.filter(brand_bussiness_opr_type='Yes'),
        'blogs':blogs,
        'social_data':social_data,
        'blogssi':blogssi,
        'non_exclusive_brands':neb,
        'head_bots':headbots,
        'body_bots':bodybots,
    }
    if request.method=="POST":
        firstName=request.POST['firstName']
        lastName=request.POST['lastName']
        phone=request.POST['phone']
        fCategoryEmail=request.POST['fCategoryEmail']
        InvestmentAmount=request.POST['InvestmentAmount']
        category_id=request.POST['category_id']
        completeAddress=request.POST['completeAddress']
        cat_inquery.objects.create(category_id=category.objects.get(id=category_id),firstName=firstName,lastName=lastName,phone=phone,fCategoryEmail=fCategoryEmail,InvestmentAmount=InvestmentAmount,completeAddress=completeAddress)

    # print(about_data.footer_content)
    return render(request,'front-end/category-automotive.html',context)

#@cache_page(CACHE_TTL)
def front_brand(request,bk):
    # home_details=Home_Details.objects.get()
    category_data=category.objects.all()
    headbots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=1).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='brand_page')).all()
    bodybots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=2).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='brand_page')).all()

    brand_type=request.GET.get('type')
    if brand_type!="neb":
        brand_data1=brand.objects.get(brand_slug=bk)
        gallery=json.loads(brand_data1.brand_gallery)
        royalty=[]
        royalty_type=json.loads(brand_data1.brand_royalty_type)
        royalty_fee=json.loads(brand_data1.brand_royalty_fee)
        for i in range(0,len(json.loads(brand_data1.brand_royalty_type))):
            royalty.append({
                'royalty_type':royalty_type[i],
                'royalty_fee': royalty_fee[i]
            })
    elif brand_type=="neb":
        brand_data1=NonExclusiveBrands.objects.get(brand_slug=bk)
        gallery=""
        royalty_type=""
        royalty_fee=""
        royalty=""

    brands=brand.objects.all()
    blogs=blog.objects.all().order_by('-post_date')
    social_data=social_link.objects.get()

    context={
        # 'home_details':home_details,
        'category_data':category_data,
        'brand_data1':brand_data1,
        # 'brands':brands.filter(category_id=pk),
        'top_bussiness':brands.filter(brand_bussiness_opr_type='Yes'),
        'blogs':blogs[:2],
        'gallery':gallery,
        'social_data':social_data,
        'royalty':royalty,
        'head_bots':headbots,
        'body_bots':bodybots,
        
    }
    if request.method=="POST":
        firstName=request.POST['firstName']
        lastName=request.POST['lastName']
        phone=request.POST['phone']
        fBrandEmail=request.POST['fBrandEmail']
        InvestmentAmount=request.POST['InvestmentAmount']
        brand_id=request.POST['brand_id']
        completeAddress=request.POST['completeAddress']
        brand_inquery.objects.create(brand_id=brand.objects.get(id=brand_id),firstName=firstName,lastName=lastName,phone=phone,fBrandEmail=fBrandEmail,InvestmentAmount=InvestmentAmount,completeAddress=completeAddress)

    # print(about_data.footer_content)
    return render(request,'front-end/single-exclusive-brands.html',context)

#@cache_page(CACHE_TTL)
def front_upcoming_event(request, id):
    # home_details=Home_Details.objects.get()
    about_data=about_sec.objects.get()
    category_data=category.objects.all()
    category_data=category.objects.all()
    brand_data1=brand.objects.all()
    brands=brand.objects.all()
    # blogs=blog.objects.all().order_by('-post_date')
    blogsall=blog.objects.all().order_by('-post_date')
    events=event.objects.filter(id=id).all()
    social_data=social_link.objects.get()
    context={
        # 'home_details':home_details,
        'about_data':about_data,
        'category_data':category_data,
        'brand_data1':brand_data1,
        # 'events':events[:1],
        'events':events,
        "event_gallery":json.loads(events[0].pre_event_image),
        'top_bussiness':brands.filter(brand_bussiness_opr_type='Yes'),
        'blogs':blogsall[0],
        'blogsall':blogsall[1:],
        'social_data':social_data,
    }    
    if events[0].event_status.lower()=="no":
        return render(request,'front-end/previous-event.html',context)
    else:
        return render(request,'front-end/upcoming-event.html',context)

#@cache_page(CACHE_TTL)
def front_single_blog(request,blk):
    # home_details=Home_Details.objects.get()
    about_data=about_sec.objects.get()
    category_data=category.objects.all()
    category_data=category.objects.all()
    brand_data1=brand.objects.all()
    brands=brand.objects.all()
    blogss=blog.objects.get(blog_slug=blk)
    blogsall=blog.objects.all().order_by('-post_date')
    events=event.objects.all()
    social_data=social_link.objects.get()

    headbots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=1).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='blog')).all()
    bodybots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=2).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='blog')).all()
    

    context={
        # 'home_details':home_details,
        'about_data':about_data,
        'category_data':category_data,
        'brand_data1':brand_data1,
        'events':events[:1],
        'top_bussiness':brands.filter(brand_bussiness_opr_type='Yes'),
        'blogs':blogsall[0],
        'blogsall':blogsall[1:],
        'blogss':blogss,
        'social_data':social_data,
        'head_bots':headbots,
        'body_bots':bodybots,
    }    
    return render(request,'front-end/single-blog-1.html',context)

#@cache_page(CACHE_TTL)
def franchise_directory(request):    
    # home_details=Home_Details.objects.get()   
    category_data=category.objects.all().order_by('id')
    brands=list(brand.objects.all())
    non_exclusive_brands=NonExclusiveBrands.objects.all()
    headbots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=1).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='fr_directory_page')).all()
    bodybots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=2).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='fr_directory_page')).all()

    context={
        # 'home_details':home_details,        
        'category_data':category_data,
        'brand_data':brands,  
        'non_exclusive_brands':non_exclusive_brands,
        'head_bots':headbots,
        'body_bots':bodybots,      
    }    
   
    return render(request,'front-end/franchise-category.html',context)

#@cache_page(CACHE_TTL)
def all_bussiness_opp(request):
    # home_details=Home_Details.objects.get()
    about_data=about_sec.objects.get()
    category_data=category.objects.all()
    category_data=category.objects.all()
    brand_data1=brand.objects.all()
    brands=brand.objects.all()
    # blogss=blog.objects.get(id=blk)
    blogsall=blog.objects.all().order_by('-post_date')
    events=event.objects.all()
    social_data=social_link.objects.get()
    

    context={
        # 'home_details':home_details,
        'about_data':about_data,
        'category_data':category_data,
        'brand_data1':brand_data1,
        'events':events[:1],
        'top_bussiness':brands.filter(brand_bussiness_opr_type='Yes'),
        'blogs':blogsall[0],
        'blogsall':blogsall[1:],
        # 'blogss':blogss,
        'social_data':social_data,
    }    
    # print(about_data.footer_content)
    return render(request,'front-end/top-business-opp-and-featured-brands.html',context)

#@cache_page(CACHE_TTL)
def all_featured_brands(request):
    # home_details=Home_Details.objects.get()
    about_data=about_sec.objects.get()
    category_data=category.objects.all()
    category_data=category.objects.all()
    brand_data1=brand.objects.all()
    brands=brand.objects.all()
    # blogss=blog.objects.get(id=blk)
    blogsall=blog.objects.all().order_by('-post_date')
    events=event.objects.all()
    social_data=social_link.objects.get()
    
    headbots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=1).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='featured_brands')).all()
    bodybots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=2).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='featured_brands')).all()
    
    context={
        # 'home_details':home_details,
        'about_data':about_data,
        'category_data':category_data,
        'brand_data1':brand_data1,
        'events':events[:1],
        'all_featured_brands':brands.filter(brand_featured_type='Yes'),
        'blogs':blogsall[0],
        'blogsall':blogsall[1:],
        # 'blogss':blogss,
        'social_data':social_data,
        'head_bots':headbots,
        'body_bots':bodybots,
    }    
    return render(request,'front-end/top-featured-brands.html',context)

#@cache_page(CACHE_TTL)
def all_food_beverages(request):
    # home_details=Home_Details.objects.get()
    about_data=about_sec.objects.get()
    category_data=category.objects.all()
    category_data=category.objects.all()
    brand_data1=brand.objects.all()
    brands=brand.objects.all()
    review_data=review.objects.all().order_by
    # blogs=blog.objects.all().order_by('-post_date')
    blogsall=blog.objects.all().order_by('-post_date')
    events=event.objects.all()
    social_data=social_link.objects.get()   
    context={
        # 'home_details':home_details,
        'about_data':about_data,
        'category_data':category_data,
        'brands_food_filter':brands.filter(id=7),
        'brand_data1':brand_data1,
        'pre_event_data':events.filter(event_status='No'),
        'up_event_data':events.filter(event_status='Yes'),
        'top_bussiness':brands.filter(brand_bussiness_opr_type='Yes'),
        'featured_brand':brands.filter(brand_featured_type='Yes'),
        'blogs':blogsall[0],
        'blogsall':blogsall[1:],
        'social_data':social_data,
        'review_data':review_data,
        'food_bev':brands.filter(category_id=7),
    }   
    # print(about_data.footer_content)
    return render(request,'front-end/food-beverages.html',context)


def list_your_brand(request):
    # home_details=Home_Details.objects.get() 
    category_data=category.objects.all()  
    social_data=social_link.objects.get()
    msg="Data Submit Successfully Thank you for connecting"
    context={
        # 'home_details':home_details,        
        'social_data':social_data,
        'category_data':category_data,       
    }  
    if request.method=="POST":       
        f_name=request.POST['f_name']
        l_name=request.POST['f_name']  
        email=request.POST['email']
        mobile=request.POST['mobile']
        representative_type=request.POST['representative_type']
        compnay_name=request.POST['compnay_name']
        corporate_number=request.POST['corporate_number']
        compnay_director_name=request.POST['compnay_director_name']
        franchise_head=request.POST['franchise_head']
        brand_name=request.POST['brand_name']
        brand_website=request.POST['brand_website']
        url_name_on_fb=request.POST['url_name_on_fb']
        headquarter_country_name=request.POST['headquarter_country_name']
        headquarter_state_name=request.POST['headquarter_state_name']
        headquarter_city_name=request.POST['headquarter_city_name']
        headquarter_pincode=request.POST['headquarter_pincode']
        headquarter_address=request.POST['headquarter_address']
        about_brand=request.POST['about_brand']
        brand_start_date=request.POST['brand_start_date']
        franchise_strat_date=request.POST['franchise_strat_date']
        franchise_operation_in_country=request.POST['franchise_operation_in_country']
        owned_outlets=request.POST['owned_outlets']
        otp=randint(000000,999999)
        data=list_ur_brand.objects.create(f_name=f_name,l_name=l_name,email=email,mobile=mobile,representative_type=representative_type,compnay_name=compnay_name,corporate_number=corporate_number,compnay_director_name=compnay_director_name,franchise_head=franchise_head,brand_name=brand_name,brand_website=brand_website,url_name_on_fb=url_name_on_fb,headquarter_country_name=headquarter_country_name,headquarter_state_name=headquarter_state_name,headquarter_city_name=headquarter_city_name,headquarter_pincode=headquarter_pincode,headquarter_address=headquarter_address,about_brand=about_brand,brand_start_date=brand_start_date,franchise_strat_date=franchise_strat_date,franchise_operation_in_country=franchise_operation_in_country,owned_outlets=owned_outlets,otp=otp) 
        return render(request,'front-end/list-your-brand.html',{'msg':msg,'category_data':category_data})
    return render(request,'front-end/list-your-brand.html',context)

def become_an_investor(request):
    # home_details=Home_Details.objects.get()
    about_data=about_sec.objects.get()
    category_data=category.objects.all()
    # category_data=category.objects.all()
    brand_data1=brand.objects.all()
    brands=brand.objects.all()
    # blogss=blog.objects.get(id=blk)
    blogsall=blog.objects.all().order_by('-post_date')
    events=event.objects.all()
    social_data=social_link.objects.get()  
    msg="Your Brand Registaration Data Submit Sucessfully We are touch after few time Thank you"
    context={
        # 'home_details':home_details,
        'about_data':about_data,
        'category_data':category_data,
        'brand_data1':brand_data1,
        'events':events[:1],
        'all_featured_brands':brands.filter(brand_featured_type='Yes'),
        'blogs':blogsall[0],
        'blogsall':blogsall[1:],
        # 'blogss':blogss,
        'social_data':social_data,
    } 
    if request.method=="POST":
        category_id=request.POST['category_id']
        full_name=request.POST['full_name']
        corporate_name=request.POST['corporate_name']
        country_name=request.POST['country_name']
        state_name=request.POST['state_name']
        city_name=request.POST['city_name']
        pincode=request.POST['pincode']
        full_address=request.POST['full_address']
        pan_number=request.POST['pan_number']
        mobile_number=request.POST['mobile_number']
        email=request.POST['email']
        website=request.POST['website']
        academic_qualification=request.POST['academic_qualification']
        age=request.POST['age']
        nature_bussiness=request.POST['nature_bussiness']
        experiance=request.POST['experiance']
        profile_intrested=request.POST['profile_intrested']
        no_of_arrangment=request.POST['no_of_arrangment']
        
        bussiness_partener_type=request.POST['bussiness_partener_type']
        bpt_full_name=request.POST['bpt_full_name']
        bpt_mobile_no=request.POST['bpt_mobile_no']
        bpt_email=request.POST['bpt_email']
        bpt_pan=request.POST['bpt_pan']
        bpt_resion_for_choose=request.POST['bpt_resion_for_choose']
        industry_exp_type=request.POST['industry_exp_type']
        elaborate=request.POST['elaborate']
        franchise_inv_range=request.POST['franchise_inv_range']
        membership_detail=request.POST['membership_detail']
        finance_type=request.POST['finance_type']
        preferd_location=request.POST['preferd_location']
        bussiness_run_type=request.POST['bussiness_run_type']
        bussiness_run_type_details=request.POST['bussiness_run_type_details']
        bussiness_reference_name=''
        bussiness_reference_email=''
        bussiness_reference_phone=''
        personal_reference_name=''
        personal_reference_email=''
        personal_reference_phone=''
        for i in request.POST.getlist('bussiness_reference_name[]'):
            bussiness_reference_name=json.dumps(request.POST.getlist('bussiness_reference_name[]'))

        for j in request.POST.getlist('bussiness_reference_email[]'):
            bussiness_reference_email=json.dumps(request.POST.getlist('bussiness_reference_email[]'))

        for k in request.POST.getlist('bussiness_reference_phone[]'):
            bussiness_reference_phone=json.dumps(request.POST.getlist('bussiness_reference_phone[]'))

        for l in request.POST.getlist('personal_reference_name[]'):
            personal_reference_name=json.dumps(request.POST.getlist('personal_reference_name[]'))

        for m in request.POST.getlist('personal_reference_email[]'):
            personal_reference_email=json.dumps(request.POST.getlist('personal_reference_email[]'))

        for n in request.POST.getlist('personal_reference_phone[]'):
            personal_reference_phone=json.dumps(request.POST.getlist('personal_reference_phone[]'))

        # bussiness_reference_name=request.POST['bussiness_reference_name']
        # bussiness_reference_email=request.POST['bussiness_reference_email']
        # bussiness_reference_phone=request.POST['bussiness_reference_phone']
        # personal_reference_name=request.POST['personal_reference_name']
        # personal_reference_email=request.POST['personal_reference_email']
        # personal_reference_phone=request.POST['personal_reference_phone']
        time_to_start_business=request.POST['time_to_start_business']
        otp=randint(000000,999999)
        data=invester_details.objects.create(category_id=category.objects.get(id=category_id),full_name=full_name,corporate_name=corporate_name,country_name=country_name,state_name=state_name,city_name=city_name,pincode=pincode,full_address=full_address,pan_number=pan_number,mobile_number=mobile_number,email=email,website=website,academic_qualification=academic_qualification,age=age,nature_bussiness=nature_bussiness,experiance=experiance,profile_intrested=profile_intrested,no_of_arrangment=no_of_arrangment,bussiness_partener_type=bussiness_partener_type,bpt_full_name=bpt_full_name,bpt_mobile_no=bpt_mobile_no,bpt_email=bpt_email,bpt_pan=bpt_pan,bpt_resion_for_choose=bpt_resion_for_choose,industry_exp_type=industry_exp_type,elaborate=elaborate,franchise_inv_range=franchise_inv_range,membership_detail=membership_detail,finance_type=finance_type,preferd_location=preferd_location,bussiness_run_type=bussiness_run_type,bussiness_run_type_details=bussiness_run_type_details,bussiness_reference_name=bussiness_reference_name,bussiness_reference_email=bussiness_reference_email,bussiness_reference_phone=bussiness_reference_phone,personal_reference_name=personal_reference_name,personal_reference_email=personal_reference_email,personal_reference_phone=personal_reference_phone,time_to_start_business=time_to_start_business,otp=otp)
        try:            
            return render(request,'front-end/become-an-investor.html',{'msg':msg,'category_data':category_data,'social_data':social_data})
        except:
            pass
            return redirect(become_an_investor)
        
    return render(request,'front-end/become-an-investor.html',context)

def contact(request):
    contact_data=contactus.objects.all()
    # home_details=Home_Details.objects.get()    
    category_data=category.objects.all()   
    brand_data1=brand.objects.all()   
    social_data=social_link.objects.get()  
    # msg="Your  Data Submit Sucessfully We are touch after few time Thank you"
    headbots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=1).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='contact_us')).all()
    bodybots=Site_Bots.objects.filter(is_bot_active=1).filter(bot_position=2).filter(Q(bot_display_on__icontains='all') | Q(bot_display_on__icontains='contact_us')).all()

    context={
        # 'home_details':home_details,        
        'category_data':category_data,
        'brand_data1':brand_data1,
        'social_data':social_data,
        'contact_data':contact_data,
        'head_bots':headbots,
        'body_bots':bodybots,
    }
    
    if request.method=="POST":
        # print(request.POST)
        category_id=request.POST['category_id']
        full_name=request.POST['full_name']
        mobile=request.POST['mobile']
        email=request.POST['email']
        investment=request.POST['investment']
        details=request.POST['details']      
        contactus.objects.create(category_id=category.objects.get(id=category_id),full_name=full_name,mobile=mobile,email=email,investment=investment,details=details)
          
    return render(request,'front-end/contact.html',context)



def consultancy_form(request):
    # home_details=Home_Details.objects.get()
    category_data=category.objects.all()
    # category_data1=category.objects.get(id=pk)
    brands=brand.objects.all()
    blogs=blog.objects.all()
    blogssi=blog.objects.all().order_by('-id')[0:2]
    social_data=social_link.objects.get()
    # print(blogs)
    context={
        # 'home_details':home_details,
        'category_data':category_data,
        # 'category_data1':category_data1,
        # 'brands':brands.filter(category_id=pk),
        'top_bussiness':brands.filter(brand_bussiness_opr_type='Yes'),
        'blogs':blogs,
        'social_data':social_data,
        'blogssi':blogssi,
    }

    if request.method=="POST":
        name=request.POST['name']
        phone=request.POST['phone']
        email=request.POST['email']
        pin=request.POST['pin']
        message=request.POST['message']
        consultancy.objects.create(name=name,phone=phone,email=email,pin=pin,message=message)
    # print(about_data.footer_content)
    return render(request,'front-end/footer.html',context)

def newsletter_form(request):
    # home_details=Home_Details.objects.get()
    category_data=category.objects.all()
    # category_data1=category.objects.get(id=pk)
    brands=brand.objects.all()
    blogs=blog.objects.all()
    blogssi=blog.objects.all().order_by('-id')[0:2]
    social_data=social_link.objects.get()
    # print(blogs)
    context={
        # 'home_details':home_details,
        'category_data':category_data,
        # 'category_data1':category_data1,
        # 'brands':brands.filter(category_id=pk),
        'top_bussiness':brands.filter(brand_bussiness_opr_type='Yes'),
        'blogs':blogs,
        'social_data':social_data,
        'blogssi':blogssi,
    }
    if request.method=="POST":        
        email=request.POST['email']       
        newsletters.objects.create(email=email)
    # print(about_data.footer_content)
    return render(request,'front-end/footer.html',context)


def dir_inquery_form(request):
    if request.method == "GET":
        return redirect("franchise_directory")
    
    elif request.method =="POST":
        # print(request.POST)
        if 'brand_type' in request.POST:
            brand_type=request.POST['brand_type']
        else:
            brand_type="eb"
        dir_inq_obj=dir_inquery(
                category_id=request.POST['category_id'],
                brand_id=request.POST['brand_id'],
                fullname=request.POST['full_name'],
                phone=request.POST['mobile'],
                email=request.POST['email'],
                city=request.POST['city'],
                InvestmentAmount=request.POST['investment'],
                brand_type=brand_type
                )
        dir_inq_obj.save()
        if 'next' in request.POST:
            # print("next is:", request.POST['next'])
            return redirect(request.POST['next'])
        return redirect("franchise_directory")

def createNote(request):
    if request.method == 'POST': 
        title = request.POST.get('title') 
        note = request.POST.get('note')
    return JsonResponse({"status": 'Success'}) 
# ./ axios code to Handling Post 


def sitemapView(request):
    file_path=str(settings.BASE_DIR)+"/files/"+'sitemap.xml'
    with open(file_path, 'r') as f:
        xml = f.read()
    response = HttpResponse(xml, content_type='application/xml')
    return response



def robotsTxtView(request):
    file_path=str(settings.BASE_DIR)+"/files/"+'robots.txt'
    with open(file_path, 'r') as f:
        text = f.read()
    response = HttpResponse(text, content_type='text')
    return response







# ============================ APIs ====================================================================
class BrandAPIview(APIView):
    ACCESS_KEY="e7a33a1e-031e-4a63-92ac-41c8c7fbb3795ca115fb-8198-4a0f-9864-e8c184528b85d5757995-c002-42e2-98de-cea4ecd6b5a7"
    
    def get(self,request, *args, **kwargs):
        key=request.GET.get('key')
        if key is None or key != self.ACCESS_KEY:
            return Response({'detail':'Invalid Access Key'},status=400)
        data=brand.objects.values().all()
        return Response(data,status=200)

class CategoryAPIview(APIView):
    ACCESS_KEY="e7a33a1e-031e-4a63-92ac-41c8c7fbb3795ca115fb-8198-4a0f-9864-e8c184528b85d5757995-c002-42e2-98de-cea4ecd6b5a7"
    
    def get(self,request, *args, **kwargs):
        key=request.GET.get('key')
        if key is None or key != self.ACCESS_KEY:
            return Response({'detail':'Invalid Access Key'},status=400)
        data=category.objects.values().all()
        return Response(data,status=200)

