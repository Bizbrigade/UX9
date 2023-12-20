from django.core.validators import FileExtensionValidator
from distutils.command.upload import upload
from email.policy import default
from pyexpat import model
from unittest.util import _MAX_LENGTH
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid

# from ckeditor.fields import RichTextField

# Create your models here.
# class Home(models.Model):
#     id=models.IntegerField(primary_key=True,default=1)
#     logo=models.ImageField(upload_to="images/")
#     banner_img1=models.ImageField(upload_to="images/")
#     banner_img2=models.ImageField(upload_to="images/")
#     banner_img3=models.ImageField(upload_to="images/")
#     about_content=models.TextField(max_length=10000)
#     about_head=models.CharField(max_length=100)
#     about_banner_img=models.ImageField(upload_to="images/",blank=True)
#     about_footer_content=models.TextField(max_length=10000)
#     email=models.TextField(max_length=300, default="#")
#     mobile=models.BigIntegerField(default='0000000000')
#     address=models.CharField(max_length=300,default='#')
#     facebook=models.TextField(max_length=300, default="#")
#     insta=models.TextField(max_length=300,default="#")
#     linkedin=models.TextField(max_length=300,default="#")
#     whatsapp=models.TextField(max_length=300,default="#")
#     youtube=models.TextField(max_length=300,default="#")

class Home_Details(models.Model):
    logo=models.ImageField(upload_to="images/",default='#')
    banner1=models.ImageField(upload_to="images/",default='#')
    banner2=models.ImageField(upload_to="images/",default='#')
    banner3=models.ImageField(upload_to="images/",default='#')
    Phone=models.BigIntegerField(default='0000000000')
    email=models.EmailField(max_length=50, default="#")
    address=models.CharField(max_length=150, default="#")
    location=models.CharField(max_length=150, default="#")
    address=models.CharField(max_length=150, default="#")
    pp=models.TextField(max_length=500, default="#")
    tc=models.TextField(max_length=500, default="#")
    rc=models.TextField(max_length=500, default="#")
    home_dateils_post_date=models.DateTimeField(default=timezone.now)

class social_link(models.Model):
    youtube=models.CharField(max_length=50, default="#")
    facebook=models.CharField(max_length=50, default="#")
    instagram=models.CharField(max_length=50, default="#")
    linkedin=models.CharField(max_length=50, default="#")
    whatsup=models.CharField(max_length=50, default="#")
    social_link_post_date=models.DateTimeField(default=timezone.now)

class about_sec(models.Model):
    head=models.CharField(max_length=50,default='#')
    about_post_date=models.DateTimeField(default=timezone.now)
    footer_content=models.CharField(max_length=50,default='#')
    page_content=models.TextField(max_length=50,default='#')
    about_banner=models.ImageField(upload_to="images/about/",default='#')
    about_seo_sec=models.CharField(max_length=50,default='#')

class blog(models.Model):
    blog_title=models.CharField(max_length=250, default='#')
    blog_slug=models.TextField(default='#')
    post_date=models.DateTimeField(default=timezone.now)
    blog_content=models.TextField(default='#')
    blog_image=models.ImageField(upload_to="images/blog/",default='#')
    blog_seo_keywords=models.CharField(max_length=2048,default='#')
    blog_seo_title = models.TextField(default='#')
    blog_seo_description = models.TextField(default='#')
    blog_script=models.TextField(default='')
    logs            =   models.TextField(default='#')

class event(models.Model):
    event_title=models.CharField(max_length=250, default='#')
    event_date=models.DateTimeField(default=timezone.now)
    event_content=models.TextField(default='#')
    event_status=models.CharField(max_length=20)
    event_url   =   models.TextField(default="#")
    event_image=models.CharField(max_length=500,default='#')
    pre_event_image=models.CharField(max_length=500,default='#')
    event_seo=models.CharField(max_length=50,default='#') 
    
class review(models.Model):
    review_name=models.CharField(max_length=250, default='#')
    review_date=models.DateTimeField(default=timezone.now)
    review_content=models.TextField(default='#')
    review_status=models.CharField(max_length=20)
    review_image=models.ImageField(upload_to="images/review/",default='#')
    review_video = models.FileField(upload_to='images/review/video/',validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])],default='#')
    text_review= models.BooleanField(default=True)
    # review_video=models.FileField(upload_to='images/review',max_length=500,default='#')


class category(models.Model):
    category_name=models.CharField(max_length=250, default='#')
    category_slug=models.TextField(default='#')
    category_date=models.DateTimeField(default=timezone.now)
    about_category=models.TextField(default='#')
    category_banner_image=models.ImageField(upload_to="images/category/",default='#')
    category_home_image=models.ImageField(upload_to="images/category/",default='#')
    logs             = models.TextField(default='#')
    category_seo_title = models.TextField(default='#')
    category_seo_description = models.TextField( default='#')
    category_script=models.TextField(default=' ')
    category_seo_keywords=models.TextField(default='#')
    category_script_position=models.IntegerField(default=2)
    #POSITION: 1 -- > Head
    #POSITION: 2 -- > Body

    def __int__(self):
        return self.id

class brand(models.Model):
    brand_name=models.CharField(max_length=100,default='#')
    brand_slug=models.TextField(default='#')
    category_id=models.ForeignKey(category,on_delete=models.CASCADE)
    brand_logo=models.ImageField(upload_to="images/brand/",default='#')
    brand_outlets=models.BigIntegerField()
    brand_about=models.TextField()
    brand_whyus=models.TextField()
    brand_op_cmd_yr=models.BigIntegerField()
    brand_fr_cmd_yr=models.BigIntegerField()
    brand_inv_min=models.BigIntegerField()
    brand_inv_min_type=models.CharField(max_length=50,default='#')
    brand_inv_max=models.BigIntegerField()
    brand_inv_max_type=models.CharField(max_length=50,default='#')
    brand_fr_fee=models.BigIntegerField()
    brand_royalty_type=models.CharField(max_length=100,default='#')
    brand_royalty_fee=models.CharField(max_length=100,default='#')
    brand_master_fr_fee=models.BigIntegerField(default=0)
    brand_territorial_rights=models.CharField(max_length=50,default='#')
    brand_anticipated_percent=models.BigIntegerField()
    brand_payback_min=models.IntegerField()
    brand_payback_max=models.IntegerField()
    brand_payback_min_type=models.CharField(max_length=50,default='year')
    brand_payback_max_type=models.CharField(max_length=50,default='year')
    brand_investment_requir=models.BigIntegerField()
    brand_fr_terms_yr=models.IntegerField()
    brand_renewable=models.CharField(max_length=50,default='#')
    brand_property_required=models.CharField(max_length=100,default='#')
    brand_floor_area_min=models.IntegerField()
    brand_floor_area_max=models.IntegerField()
    brand_fre_location_outlets=models.CharField(max_length=100,default='#')
    brand_fre_location_masters=models.CharField(max_length=100,default='#')
    brand_operating_type=models.CharField(max_length=50,default='#')
    brand_fre_training_location=models.CharField(max_length=100,default='#')
    brand_assistece_available_type=models.CharField(max_length=50,default='#')
    brand_head_office_gyd_type=models.CharField(max_length=50,default='#')
    brand_it_system_type=models.CharField(max_length=50,default='#')
    brand_bussiness_opr_type=models.CharField(max_length=50,default='#')
    brand_featured_type=models.CharField(max_length=50,default='#')
    brand_gallery=models.CharField(max_length=500,default='#')
    brand_seo_keywords=models.CharField(max_length=100,default='#')
    brand_seo_title=models.TextField(default='#')
    brand_seo_description=models.TextField(default='#')
    brand_script=models.TextField(default='')
    brand_script_position=models.IntegerField(default=2)
    brand_ismasterfranchaise=models.CharField(max_length=3, default='no')
    brand_master_investment_min=models.IntegerField()
    brand_master_investment_min_type=models.CharField(max_length=5,default='#')
    brand_master_investment_max=models.IntegerField()
    brand_master_investment_max_type=models.CharField(max_length=5,default='#')
    brand_master_exclusive_city_rights=models.CharField(max_length=3, default='no')
    brand_master_exclusive_region_rights=models.CharField(max_length=3, default='no')
    brand_master_exclusive_state_rights=models.CharField(max_length=3, default='no')
    brand_master_royalty_share=models.CharField(max_length=3, default='no')
    brand_master_distribution_margin=models.CharField(max_length=3, default='no')
    brand_master_franchise_fee_share=models.CharField(max_length=3, default='no')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    logs       = models.TextField(default='#')

    def __int__(self):
        return self.category_id,self.id

        
class NonExclusiveBrands(models.Model):
    id=models.TextField(primary_key=True)
    brand_name=models.CharField(max_length=100,default='#')
    brand_slug=models.TextField(default='#')
    category_id=models.IntegerField() #ForeignKey(category,on_delete=models.CASCADE)
    brand_logo=models.ImageField(upload_to="images/brand/",default='#')
    brand_outlets=models.BigIntegerField()
    yr_of_establish=models.IntegerField()
    brand_inv_min=models.BigIntegerField()
    brand_inv_min_type=models.CharField(max_length=50,default='#')
    brand_inv_max=models.BigIntegerField()
    brand_inv_max_type=models.CharField(max_length=50,default='#')
    brand_payback_min=models.IntegerField()
    brand_payback_min_type=models.CharField(max_length=50,default='year')
    brand_payback_max_type=models.CharField(max_length=50,default='year')
    brand_payback_max=models.IntegerField()
    brand_floor_area_min=models.IntegerField()
    brand_floor_area_max=models.IntegerField()
    brand_show_on_homepage=models.CharField(max_length=1,default="0")   #Note: Boolean field cause ERROR while filtering
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    logs            =   models.TextField(default='#')
    # brand_about=models.TextField()
    # brand_whyus=models.TextField()
    # brand_op_cmd_yr=models.BigIntegerField()
    # brand_fr_cmd_yr=models.BigIntegerField()
    # brand_fr_fee=models.BigIntegerField()
    # brand_royalty_type=models.CharField(max_length=100,default='#')
    # brand_royalty_fee=models.CharField(max_length=100,default='#')
    # brand_master_fr_fee=models.BigIntegerField()
    # brand_territorial_rights=models.CharField(max_length=50,default='#')
    # brand_anticipated_percent=models.BigIntegerField()

    # brand_investment_requir=models.BigIntegerField()
    # brand_fr_terms_yr=models.IntegerField()
    # brand_renewable=models.CharField(max_length=50,default='#')
    # brand_property_required=models.CharField(max_length=100,default='#')
    # brand_fre_location_outlets=models.CharField(max_length=100,default='#')
    # brand_fre_location_masters=models.CharField(max_length=100,default='#')
    # brand_operating_type=models.CharField(max_length=50,default='#')
    # brand_fre_training_location=models.CharField(max_length=100,default='#')
    # brand_assistece_available_type=models.CharField(max_length=50,default='#')
    # brand_head_office_gyd_type=models.CharField(max_length=50,default='#')
    # brand_it_system_type=models.CharField(max_length=50,default='#')
    # brand_bussiness_opr_type=models.CharField(max_length=50,default='#')
    # brand_featured_type=models.CharField(max_length=50,default='#')
    # brand_gallery=models.CharField(max_length=500,default='#')
    # brand_seo_keywords=models.CharField(max_length=100,default='#')
    def __int__(self):
        return self.category_id,self.id

class list_ur_brand(models.Model):
    f_name=models.CharField(max_length=50,default='#')
    l_name=models.CharField(max_length=50,default='#')
    email=models.EmailField(max_length=50,default='#')
    mobile=models.BigIntegerField(default=0000000000)
    representative_type=models.CharField(max_length=50,default='#')
    compnay_name=models.CharField(max_length=50,default='#')
    corporate_number=models.CharField(max_length=10,default='0000000000')
    compnay_director_name=models.CharField(max_length=50,default='#')
    franchise_head=models.CharField(max_length=50,default='#')
    brand_name=models.CharField(max_length=50,default='#')
    brand_website=models.URLField(max_length=50,default='#')
    url_name_on_fb=models.CharField(max_length=50,default='#')
    headquarter_country_name=models.CharField(max_length=50,default='#')
    headquarter_state_name=models.CharField(max_length=50,default='#')
    headquarter_city_name=models.CharField(max_length=50,default='#')
    headquarter_pincode=models.BigIntegerField(default=0000000000)
    headquarter_address=models.CharField(max_length=50,default='#')
    about_brand=models.TextField(max_length=50,default='#')
    brand_start_date=models.DateField(default='date')
    franchise_strat_date=models.DateField(default='date')
    franchise_operation_in_country=models.CharField(max_length=50,default='#')
    owned_outlets=models.CharField(max_length=50,default='#')
    submition_date=models.DateField(auto_now=True)
    otp=models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class invester_details(models.Model):
    category_id=models.ForeignKey(category,on_delete=models.CASCADE)
    full_name=models.CharField(max_length=50,default='#')
    corporate_name=models.CharField(max_length=50,default='#')
    country_name=models.CharField(max_length=50,default='#')
    state_name=models.CharField(max_length=50,default='#')
    city_name=models.CharField(max_length=50,default='#')
    pincode=models.IntegerField()
    full_address=models.TextField()
    pan_number=models.CharField(max_length=10,default='#')
    mobile_number=models.BigIntegerField(default=0000000000)
    email=models.EmailField(max_length=50,default='#')
    website=models.URLField(max_length=50,default='#')
    academic_qualification=models.CharField(max_length=50,default='#')
    age=models.IntegerField()
    nature_bussiness=models.CharField(max_length=50,default='#')
    experiance=models.CharField(max_length=50,default='#')
    profile_intrested=models.CharField(max_length=50,default='#')
    no_of_arrangment=models.CharField(max_length=50,default='#')
    bussiness_partener_type=models.CharField(max_length=50,default='#')
    bpt_full_name=models.CharField(max_length=50,default='#')
    bpt_mobile_no=models.BigIntegerField(default=0000000000)
    bpt_email=models.EmailField(max_length=50,default='#')
    bpt_pan=models.CharField(max_length=50,default='#')
    bpt_resion_for_choose=models.CharField(max_length=50,default='#')
    industry_exp_type=models.CharField(max_length=50,default='#')
    elaborate=models.CharField(max_length=50,default='#')
    franchise_inv_range=models.CharField(max_length=50,default='#')
    membership_detail=models.CharField(max_length=50,default='#')
    finance_type=models.CharField(max_length=50,default='#')
    preferd_location=models.CharField(max_length=50,default='#')
    bussiness_run_type=models.CharField(max_length=50,default='#')
    bussiness_run_type_details=models.CharField(max_length=50,default='#')
    bussiness_reference_name=models.CharField(max_length=50,default='#')
    bussiness_reference_email=models.EmailField(max_length=50,default='#')
    bussiness_reference_phone=models.CharField(max_length=50,default='#')
    personal_reference_name=models.CharField(max_length=50,default='#')
    personal_reference_email=models.EmailField(max_length=50,default='#')
    personal_reference_phone=models.CharField(max_length=50,default='#')
    submition_date=models.DateField(auto_now=True)
    time_to_start_business=models.TextField()
    termsandcondition=models.BooleanField()
    otp=models.IntegerField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class contactus(models.Model):
    # id=models.BigIntegerField(primary_key=True, auto_created=True)
    category_id=models.ForeignKey(category,on_delete=models.CASCADE)
    full_name=models.CharField(max_length=50,default='#')
    mobile=models.BigIntegerField(default='#')
    email=models.EmailField(max_length=50,default='#')
    investment=models.CharField(max_length=50,default='#')
    details=models.CharField(max_length=50,default='#')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __int__(self):
        return self.id


class dir_inquery(models.Model):
    id=models.AutoField(primary_key=True)    
    category_id=models.IntegerField()
    brand_id=models.CharField(max_length=1024)
    fullname=models.CharField(max_length=128,default='#')
    phone=models.BigIntegerField(default='#')
    email=models.EmailField(max_length=50,default='#')
    InvestmentAmount=models.CharField(max_length=50,default='#')
    brand_type=models.CharField(max_length=64, default="eb")
    completeAddress=models.CharField(max_length=50,default='#')
    city=models.CharField(max_length=128, default="#")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __int__(self):
        return self.id


class cat_inquery(models.Model):    
    category_id=models.ForeignKey(category,on_delete=models.CASCADE)
    firstName=models.CharField(max_length=50,default='#')
    lastName=models.CharField(max_length=50,default='#')
    phone=models.BigIntegerField(default='#')
    fCategoryEmail=models.EmailField(max_length=50,default='#')
    InvestmentAmount=models.CharField(max_length=50,default='#')
    completeAddress=models.CharField(max_length=50,default='#')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __int__(self):
        return self.id

class brand_inquery(models.Model):    
    brand_id=models.ForeignKey(brand,on_delete=models.CASCADE)
    firstName=models.CharField(max_length=50,default='#')
    lastName=models.CharField(max_length=50,default='#')
    phone=models.BigIntegerField(default='#')
    fBrandEmail=models.EmailField(max_length=50,default='#')
    InvestmentAmount=models.CharField(max_length=50,default='#')
    completeAddress=models.CharField(max_length=50,default='#')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __int__(self):
        return self.id

class consultancy(models.Model):    
    name=models.CharField(max_length=50,default='#')
    phone=models.BigIntegerField(default='#')
    email=models.EmailField(max_length=50,default='#')
    pin=models.IntegerField(default='#')
    message=models.CharField(max_length=50,default='#')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __int__(self):
        return self.id

class newsletters(models.Model): 
    email=models.EmailField(max_length=50,default='#')    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __int__(self):
        return self.id


class Site_Bots(models.Model):
    id=models.AutoField(primary_key=True)
    bot_slug=models.TextField()
    bot_name=models.TextField()
    bot_script=models.TextField(default="#")
    bot_display_on=models.TextField(default="all")
    bot_position=models.IntegerField(default=2)
    is_bot_active=models.IntegerField(default=1)
    #POSITION: 1 -- > Head
    #POSITION: 2 -- > Body
    #ACTIVE : 1 -->  ACTIVE
    #ACTIVE : 0 -->  IN-ACTIVE

    # def save(self, *args, **kwargs):
    #     self.bot_slug=slugify(self.bot_name+" "+str(uuid.uuid4())[:6])
    #     super(Site_Bots,self).save(*args, **kwargs)
        # return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.bot_slug


class Articles(models.Model):
    id=models.AutoField(primary_key=True)
    article_title=models.CharField(max_length=250, default='#')
    article_slug=models.TextField(default='#')
    article_url=models.TextField(default='#')
    article_desc=models.CharField(max_length=250, default='#')
    article_img=models.ImageField(upload_to="images/blog/",default='#')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.article_slug


# User access Management 
class Notifications(models.Model):
    id=models.AutoField(primary_key=True)
    notification_title=models.CharField(max_length=250, default='#')
    notification_from=models.IntegerField()
    notification_from_role=models.CharField(max_length=16)
    notification_to=models.IntegerField()
    notification_to_role=models.CharField(max_length=16)
    notification_description=models.TextField(default='#')
    notification_url=models.TextField(default='#')
    notification_status=models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    """
    STATUS:
        1 --> New notification / Un seen notifications
        2 --> Visited / Seen notifications / Action taken 
        3 --> 
    """
    
    def __str__(self):
        return self.notification_title


class Employee(models.Model):
    id          =   models.AutoField(primary_key=True)
    firstname   =   models.CharField(max_length=255)
    lastname    =   models.CharField(max_length=255, default=' ')
    email       =   models.EmailField(max_length=255, unique=True)
    password    =   models.CharField(max_length=255)
    address     =   models.TextField(max_length=10000, default="#")
    access      =   models.TextField(max_length=10000)
    role        =   models.CharField(max_length=10, default='employee')
    is_verified =   models.IntegerField(default=0)
    is_active   =   models.IntegerField(default=1)
    is_superuser=   models.BooleanField(default=False)
    created_at  =   models.DateTimeField(auto_now_add=True)
    updated_at  =   models.DateTimeField(auto_now=True)
    last_login  =   models.DateTimeField()

    def __str__(self):
        return self.firstname + self.lastname

class Reset_Password_Requests(models.Model):
    id          =   models.AutoField(primary_key=True)
    email       =   models.CharField(max_length=255, unique=True)
    token       =   models.TextField(max_length=10000, default="#")
    created_at  =   models.DateTimeField(auto_now_add=True)
    valid_till  =   models.DateTimeField()

    def __str__(self):
        return self.user_id


# ============================== Duplicate tables for approval process ================================
# Types:
    ''' 
    insert
    update
    delete    
    '''
    # IS Approved
    '''
        0--> Not approved
        1--> Approved
        2--> Rejected
    '''
class Temp_Category(models.Model):
    id              =   models.AutoField(primary_key=True)
    category_name   =   models.CharField(max_length=250, default='#')
    category_slug=models.TextField(default='#')
    # category_date   =   models.DateTimeField(default=timezone.now)
    about_category  =   models.TextField(default='#')
    category_banner_image=models.ImageField(upload_to="images/category/",default='#')
    category_home_image=models.ImageField(upload_to="images/category/",default='#')
    category_keywords=models.CharField(max_length=400, default='#')
    task_type       =   models.CharField(max_length=16, default='insert')
    to_category_id  =   models.IntegerField(default=0)
    is_approved     =   models.IntegerField(default=0)
    actor           =   models.IntegerField(default=0)
    category_seo_title = models.TextField(default='#')
    category_seo_description = models.TextField( default='#')
    category_script=models.TextField(default=' ')
    category_seo_keywords=models.TextField(default='#')
    category_script_position=models.IntegerField(default=0)
    logs            =   models.TextField()  #{ action_type:insert, requested_by:<name>, requested_user_id:<id>,requested_at:<datetime>, 
                                            # response_by:<admin name>, response_user_id:<admin id> responsed_at:<datetime>,
                                            # update_data:[{'filed':<field_name>, 'previous_value':<value>, 'new_value':<value>}, ]}
    def __int__(self):
        return self.id


class Temp_Brand(models.Model):
    id              =   models.AutoField(primary_key=True)
    brand_name=models.CharField(max_length=100,default='#')
    brand_slug=models.TextField(default='#')
    category_id=models.ForeignKey(category,on_delete=models.CASCADE)
    brand_logo=models.ImageField(upload_to="images/brand/",default='#')
    brand_outlets=models.BigIntegerField(default=0)
    brand_about=models.TextField(default='#')
    brand_whyus=models.TextField(default='#')
    brand_op_cmd_yr=models.BigIntegerField(default=0)
    brand_fr_cmd_yr=models.BigIntegerField(default=0)
    brand_inv_min=models.BigIntegerField(default=0)
    brand_inv_min_type=models.CharField(max_length=50,default='#')
    brand_inv_max=models.BigIntegerField(default=0)
    brand_inv_max_type=models.CharField(max_length=50,default='#')
    brand_fr_fee=models.BigIntegerField(default=0)
    brand_royalty_type=models.CharField(max_length=100,default='#')
    brand_royalty_fee=models.CharField(max_length=100,default='#')
    brand_master_fr_fee=models.BigIntegerField(default=0)
    brand_territorial_rights=models.CharField(max_length=50,default='#')
    brand_anticipated_percent=models.BigIntegerField(default=0)
    brand_payback_min=models.IntegerField(default=0)
    brand_payback_max=models.IntegerField(default=0)
    brand_payback_min_type=models.CharField(max_length=50,default='#')
    brand_payback_max_type=models.CharField(max_length=50,default='#')
    brand_investment_requir=models.BigIntegerField()
    brand_fr_terms_yr=models.IntegerField(default=0)
    brand_renewable=models.CharField(max_length=50,default='#')
    brand_property_required=models.CharField(max_length=100,default='#')
    brand_floor_area_min=models.IntegerField(default=0)
    brand_floor_area_max=models.IntegerField(default=0)
    brand_fre_location_outlets=models.CharField(max_length=100,default='#')
    brand_fre_location_masters=models.CharField(max_length=100,default='#')
    brand_operating_type=models.CharField(max_length=50,default='#')
    brand_fre_training_location=models.CharField(max_length=100,default='#')
    brand_assistece_available_type=models.CharField(max_length=50,default='#')
    brand_head_office_gyd_type=models.CharField(max_length=50,default='#')
    brand_it_system_type=models.CharField(max_length=50,default='#')
    brand_bussiness_opr_type=models.CharField(max_length=50,default='#')
    brand_featured_type=models.CharField(max_length=50,default='#')
    brand_gallery=models.CharField(max_length=500,default='#')
    brand_seo_keywords=models.CharField(max_length=100,default='#')
    brand_seo_title=models.TextField(default='#')
    brand_seo_description=models.TextField(default='#')
    brand_script=models.TextField(default='#')#TextField(default='#')
    brand_script_position=models.IntegerField(default=0)
    brand_ismasterfranchaise=models.CharField(max_length=3, default='#')
    brand_master_investment_min=models.IntegerField(default=0)
    brand_master_investment_min_type=models.CharField(max_length=5,default='#')
    brand_master_investment_max=models.IntegerField(default=0)
    brand_master_investment_max_type=models.CharField(max_length=5,default='#')
    brand_master_exclusive_city_rights=models.CharField(max_length=3, default='#')
    brand_master_exclusive_region_rights=models.CharField(max_length=3, default='#')
    brand_master_exclusive_state_rights=models.CharField(max_length=3, default='#')
    brand_master_royalty_share=models.CharField(max_length=3, default='#')
    brand_master_distribution_margin=models.CharField(max_length=3, default='#')
    brand_master_franchise_fee_share=models.CharField(max_length=3, default='#')

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    
    task_type       =   models.CharField(max_length=16, default='insert')
    to_brand_id     =   models.IntegerField(default=0)
    is_approved     =   models.IntegerField(default=0)
    logs            =   models.TextField()
    actor           =   models.IntegerField(default=0)


    def __int__(self):
        return self.category_id,self.id


class Temp_NonExclusiveBrands(models.Model):
    id=models.TextField(primary_key=True)
    brand_name=models.CharField(max_length=100,default='#')
    category_id=models.IntegerField() #ForeignKey(category,on_delete=models.CASCADE)
    brand_logo=models.ImageField(upload_to="images/brand/",default='#')
    brand_outlets=models.BigIntegerField()
    yr_of_establish=models.IntegerField()
    brand_inv_min=models.BigIntegerField()
    brand_inv_min_type=models.CharField(max_length=50,default='#')
    brand_inv_max=models.BigIntegerField()
    brand_inv_max_type=models.CharField(max_length=50,default='#')
    brand_payback_min=models.IntegerField()
    brand_payback_min_type=models.CharField(max_length=50,default='#')
    brand_payback_max_type=models.CharField(max_length=50,default='#')
    brand_payback_max=models.IntegerField()
    brand_floor_area_min=models.IntegerField()
    brand_floor_area_max=models.IntegerField()
    brand_show_on_homepage=models.CharField(max_length=1,default="0")   #Note: Boolean field cause ERROR while filtering
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    actor           =   models.IntegerField(default=0)
    task_type       =   models.CharField(max_length=16, default='insert')
    to_brand_id     =   models.IntegerField(default=0)
    is_approved     =   models.IntegerField(default=0)
    logs            =   models.TextField()

    def __int__(self):
        return self.category_id,self.id


class Temp_Blog(models.Model):
    id              =   models.AutoField(primary_key=True)
    blog_title      =   models.CharField(max_length=250, default='#')
    blog_slug=models.TextField(default='#')
    # post_date       =   models.DateTimeField(default=timezone.now)
    blog_content    =   models.TextField(default='#')
    blog_image      =   models.ImageField(upload_to="images/blog/",default='#')
    blog_seo_keywords=models.CharField(max_length=2048,default='#')
    blog_seo_title = models.TextField(default='#')
    blog_seo_description = models.TextField(default='#')
    blog_script=models.TextField(default='')
    
    task_type       =   models.CharField(max_length=16, default='insert')
    to_blog_id      =   models.IntegerField(default=0)
    is_approved     =   models.IntegerField(default=0)
    logs            =   models.TextField()
    actor           =   models.IntegerField(default=0)


class TrashBin(models.Model):
    id              =   models.AutoField(primary_key=True)
    record_id       =   models.TextField()
    record_name     =   models.TextField()
    record_category =   models.TextField()
    record_data     =   models.TextField()
    record_deleted_on  = models.DateTimeField(auto_now_add=True)
    record_exists_till  =   models.DateTimeField()
    logs            =   models.TextField()