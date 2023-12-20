from pyexpat import model
from django import forms
from django.db import models
from django.forms import fields
from .models import Home_Details,about_sec,social_link,blog,event,category,brand,review,list_ur_brand,invester_details,contact_us,cat_inquery,brand_inquery,consultancy,newsletters

class HomeDetailsForm(forms.models):
    class Meta:
        model=Home_Details
        fields='__all__'

class update_logo(forms.models):
    class Meta:
        model=Home_Details
        fields=('logo')

class update_contact(forms.models):
    class Meta:
        model=Home_Details
        fields=('Phone','email','address')

class update_social_link(forms.models):
    class Meta:
        model=social_link
        fields=('Phone','email','address')

class update_banner(forms.models):
    class Meta:
        model=Home_Details
        fields=('banner1','banner2','banner3')

class update_about_sec(forms.models):
    class Meta:
        model=about_sec
        fields=('head','footer_content','page_content','about_banner')
class update_privacy_policy(forms.models):
    class Meta:
        model=Home_Details
        fields=('pp')
class update_terms_condition(forms-models):
    class Meta:
        model=Home_Details
        fields=('tc')

class add_blog(forms-models):
    class Meta:
        model=blog
        fields=('blog_title','blog_content','blog_image','blog_seo')

class add_event(forms-models):
    class Meta:
        model=event
        fields=('event_title','event_content','event_image','pre_event_image','event_date','event_status','event_seo')

class add_review(forms-models):
    class Meta:
        model=review
        fields=('review_name','review_date','review_content','review_status','review_image','review_video')

class add_category(forms-models):
    class Meta:
        model=category
        fields=('category_name','category_date','about_category','category_banner_image','category_home_image','category_keywords')

class add_brand(forms-models):
    class Meta:
        model=brand
        fields=('brand_name','category_id','brand_logo','brand_outlets','brand_featured','brand_about','brand_whyus','brand_op_cmd_yr','brand_fr_cmd_yr','brand_inv_min','brand_inv_max','brand_fr_fee','brand_royalty_type','brand_royalty_fee','brand_master_fr_fee','brand_territorial_rights','brand_anticipated_percent','brand_payback_min','brand_payback_max','brand_investment_requir','brand_fr_terms_yr','brand_renewable','brand_property_required','brand_floor_area_min','brand_floor_area_max','brand_fre_location_outlets','brand_fre_location_masters','brand_operating_type','brand_fre_training_location','brand_assistece_available_type','brand_head_office_gyd_type','brand_it_system_type','brand_bussiness_opr_type','brand_featured_type','brand_gallery','brand_seo_keywords')
class list_ur_brand(forms-models):
    class Meta:
        model=list_ur_brand
        fields=('f_name','l_name','email','mobile','representative_type','compnay_name','corporate_number','compnay_director_name','franchise_head','brand_name','brand_website','url_name_on_fb','headquarter_country_name',
        'headquarter_state_name','headquarter_city_name','headquarter_pincode','headquarter_address','about_brand','brand_start_date','franchise_strat_date','franchise_operation_in_country','owned_outlets','otp')

class invester_details(forms-models):
    class Meta:
        model=invester_details
        fields=('category_id','full_name','corporate_name','country_name','state_name','city_name','pincode','full_address','pan_number','mobile_number','email','website','academic_qualification','age','nature_bussiness','experiance','profile_intrested','no_of_arrangment','industry_type_choice','bussiness_partener_type','bpt_full_name','bpt_mobile_no','bpt_email','bpt_pan','bpt_resion_for_choose','industry_exp_type','elaborate','franchise_inv_range','membership_detail','finance_type','preferd_location','bussiness_run_type','bussiness_run_type_details','bussiness_reference_name','bussiness_reference_email','bussiness_reference_phone','personal_reference_name','personal_reference_email','personal_reference_phone','time_to_start_business','otp')

class contact_us(forms-models):
    class Meta:
        model=contact_us
        fields=('category_id','full_name','mobile','email','investment','details')

class cat_inquery(forms-models):
    class Meta:
        model=cat_inquery
        fields='__all__'

class brand_inquery(forms-models):
    class Meta:
        model=brand_inquery
        fields=('category_id','full_name','mobile','email','investment','details')

class consultancy(forms-models):
    class Meta:
        model=consultancy
        fields='__all__'

class newsletters(forms-models):
    class Meta:
        model=newsletters
        fields='__all__'