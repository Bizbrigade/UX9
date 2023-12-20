from django.utils.text import slugify
from django.db import transaction
import pandas as pd
from collections import OrderedDict
from .models import category, NonExclusiveBrands
import uuid
import os

class NonExclusinveBulkUPload():
    def __init__(self, filepath):
        self.filepath=filepath
        self.dataframe=None
        self.file_columns=None
        self.columns=["category","brand_name","brand_outlets","yr_of_establish","brand_inv_min","brand_inv_min_type",
                      "brand_inv_max","brand_inv_max_type","brand_payback_min","brand_payback_min_type",
                      "brand_payback_max_type","brand_payback_max","brand_floor_area_min","brand_floor_area_max"]
        pass

    def validator(self):
        for col in self.file_columns:
            if col not in self.columns:
                return False, f"{col} Column Is Required"
        return True, ""

    def insert_neb(self):
        msg=""
        updatation=0
        insertion=0
        try:
            self.dataframe=pd.read_excel(self.filepath)
            self.file_columns=self.dataframe.columns
            validation_status=self.validator()
            if not validation_status[0]:
                raise Exception(validation_status[1])
            data=self.dataframe.to_dict(orient='records')
            with transaction.atomic():
                for row in data:
                    row['category_id']=category.objects.get(category_name__iexact=row['category'].strip()).id
                    # If Brand Already Exists , Update the data
                    del row['category']
                    if NonExclusiveBrands.objects.filter(category_id=row['category_id'],brand_name=row['brand_name'].strip()).exists():
                        NonExclusiveBrands.objects.filter(category_id=row['category_id'],brand_name=row['brand_name'].strip()).update(**row)
                        # neb=NonExclusiveBrands.objects.get(category_id=row['category_id'],brand_name=row['brand_name'].strip())
                        # for attr, value in row.items():
                        #     setattr(neb, attr, value)
                        # neb.save()
                        print("updated")
                        updatation=updatation+1
                    else:
                    # except NonExclusiveBrands.DoesNotExist:
                        row['id']= str(uuid.uuid4())
                        row['brand_slug']=slugify(row['brand_name']+" "+str(uuid.uuid4())[:6])
                        neb=NonExclusiveBrands.objects.create(**row)
                        insertion=insertion+1
                        print("Inserted")
                    # except Exception as e:
                        # raise Exception(str(e))
            msg=str(insertion)+' Brands Created'+"  "+str(updatation)+" Brands Updated."
        except Exception as e:
            msg=str(e)
            print(msg)
        finally:
            os.remove(self.filepath)
            return msg

