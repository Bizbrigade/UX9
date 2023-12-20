from django.utils import timezone
from django.http import HttpResponse
import pandas as pd
from datetime import datetime,timedelta
from .models import contactus, consultancy, newsletters, cat_inquery, brand_inquery, dir_inquery, list_ur_brand, invester_details, category, brand, NonExclusiveBrands

formnames={
    'contact-us-form':'Contact Us Form',
    'category-inq-form':'Category Enquiry Form',
    'brand-inq-form':'Brand Enquiry Form',
    'consultancy-form':'Consultancy Form', 
    'directory-inq-form':'Directory Form',
    'news-letter-form':'News Letter Form',
    'list-ur-brand-from':'List your brand From',
    'investor-form': ' Investor Form'}

def convert_string_to_date(input_date):
    format = '%Y-%m-%d'  # The format
    return datetime.strptime(input_date, format)
 


def export_form_to_excel(formname, fromdate=None, todate=None, **kwargs):
    dates={}
    df=None
    cols=None

    # STEP-1: GETTING DATES RANGE , If dates are in string, converting them to datetime object
    if fromdate!=None:
        if isinstance(fromdate, str):
            fromdate=convert_string_to_date(fromdate)
        fromdate=timezone.make_aware(fromdate) # Making the datetime timezone aware using the default timezone
        dates['created_at__gte']=fromdate
    if todate!=None:
        if isinstance(todate, str):
            todate=convert_string_to_date(todate)
        todate=timezone.make_aware(todate) # Making the datetime timezone aware using the default timezone
        todate=todate+timedelta(days=1) # ADDed 1 day because I was filtering with datetime obj,EX: 21-10-1990 is less than 21-10-1990 10:30:30 
        dates['created_at__lte']=todate 

    response=HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename=formnames[formname]+' '+str(fromdate)[:10]+'_to_'+str(todate)[:10]+'.xlsx'
    response['Content-Disposition']=f"attachment;filename={filename}"
    
    all_categories=category.objects.all()
    all_brands=brand.objects.all()
    all_non_exclusive_brands=NonExclusiveBrands.objects.all()
    
    #STEP-2: Data collection from the database
    if formname =='contact-us-form':
        contact_us_data=contactus.objects.filter(**dates).values('category_id', 'full_name','mobile','email', 'investment', 'details', 'created_at').order_by('created_at')
        # cols=['Category Name', 'Full Name', 'Mobile Number', 'Email ID' , 'Investment', 'Details', 'Date']
        for each in contact_us_data:
            try:
                each['created_at']=each['created_at'].date()
                # each['created_at']=each['created_at'].replace(tzinfo=None)
                each['category_id']=all_categories.get(id=each['category_id']).category_name
            except Exception as e:
                pass
                # print("ERROR: (file)", __file__, e, 'con-1')
        df=pd.DataFrame(contact_us_data)
    
    elif formname =='category-inq-form':
        category_inq_data=cat_inquery.objects.filter(**dates).values('category_id', 'firstName','lastName','phone', 'fCategoryEmail','InvestmentAmount','completeAddress')
        for each in category_inq_data:
            try:
                each['category_id']=all_categories.get(id=each['category_id']).category_name
            except Exception as e:
                pass
                # print("ERROR: (file)", __file__, e, 'con-2')
        df=pd.DataFrame(category_inq_data)
    
    elif formname =='brand-inq-form':
        brand_inq_data=brand_inquery.objects.filter(**dates).values('brand_id', 'firstName','lastName','phone', 'fBrandEmail','InvestmentAmount','completeAddress')
        for each in brand_inq_data:
            try:
                each['brand_id']=all_brands.get(id=each['brand_id']).brand_name
            except Exception as e:
                pass
                # print("ERROR: (file)", __file__, e, 'con-3')
        df=pd.DataFrame(brand_inq_data)
    
    elif formname == 'consultancy-form':
        consultancy_data=consultancy.objects.filter(**dates).values('name', 'phone','email','pin',"message")
        df=pd.DataFrame(consultancy_data)
    
    elif formname == 'directory-inq-form':
        dir_inquiry_data=dir_inquery.objects.filter(**dates).values('category_id', 'brand_type','brand_id','fullname', 'phone', 'email','InvestmentAmount',"brand_type",'completeAddress','city')
        for each in dir_inquiry_data:
            try:
                each['category_id']=all_categories.get(id=each['category_id']).category_name
                if each['brand_type']=='neb':
                    each['brand_id']=all_non_exclusive_brands.get(id=each['brand_id']).brand_name
                else:
                    each['brand_id']=all_brands.get(id=each['brand_id']).brand_name
                del each['brand_type']
            except Exception as e:
                pass
                # print("ERROR: (file)", __file__, e,'con-4')
        df=pd.DataFrame(dir_inquiry_data)

    elif formname == 'news-letter-form':
        newsletter_data=newsletters.objects.filter(**dates).values('email')
        df=pd.DataFrame(newsletter_data)

    elif formname == 'list-ur-brand-from':
        list_ur_brand_data=list_ur_brand.objects.filter(**dates).values()
        for each in list_ur_brand_data:
            try:
                # del each['created_at']
                each['created_at']=each['created_at'].date()
                del each['updated_at']
                del each['id']
                del each['otp']
            except Exception as e:
                pass
                # print("ERROR: (file)", __file__, e, 'con-5')
        df=pd.DataFrame(list_ur_brand_data)
            
    elif formname == 'investor-form':
        invester_data=invester_details.objects.filter(**dates).values()
        for each in invester_data:
            try:
                each['category_id_id']=all_categories.get(id=each['category_id_id']).category_name
                each['created_at']=each['created_at'].date()
                # del each['created_at']
                del each['updated_at']
                del each['id']
                del each['otp']
            except Exception as e:
                pass
                # print("ERROR: (file)", __file__, e,'con-6')
        df=pd.DataFrame(invester_data)
    
    if df is not None:
        with pd.ExcelWriter(response) as writer:
            df.to_excel(writer,sheet_name=formnames[formname])
    return response
