from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = category
        fields = "__all__"

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = brand
        fields = "__all__"

class NonExclusiveBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = NonExclusiveBrands
        fields = "__all__"

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = blog
        fields = "__all__"




#  TEMP Tables 
class TempCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Temp_Category
        fields = "__all__"


class TempBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temp_Brand
        fields = "__all__"


class TempBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temp_Blog
        fields = "__all__"

