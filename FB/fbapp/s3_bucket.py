from http import client
from urllib import response
import boto3
import io
from PIL import Image

def list_bucket():
    buckets=boto3.client('s3')
    response=buckets.list_buckets()
    print('these are buckets')
    for bucket in response['Buckets']:
        print(f' {bucket["Name"]}')


def create_buckets(bucket_name):
    s3=boto3.client('s3')
    location ={'LocationConstraint': 'us-east-1'}
    s3.create_bucket(Bucket=bucket_name,CreateBucketConfiguration=location)
    print("New Bucket Created")

def upload_file(file_name, bucket, store_as=None):
    if store_as is None :
        store_as = file_name
    s3=boto3.client('s3')
    s3.upload_file(file_name, bucket, store_as)
    bucket_location = s3.get_bucket_location(Bucket=bucket)
    object_url = "https://{0}.s3.{1}.amazonaws.com/{2}".format(
    bucket,
   'us-east-1',
    store_as )
    return object_url

def upload_filesobj(file, bucket, store_as):
    s3=boto3.client('s3')
    s3.upload_fileobj(file,bucket,store_as)
    print('File Uploaded')

def create_folder(foldername):
    s3=boto3.client('s3')
    folder=str(foldername)+'/'
    s3.put_object(Bucket='estimateasy',Body='', Key=folder)
    print('Folder Created',foldername)

def image_from_s3(bucket,key):
    s3=boto3.resource('s3')
    bucket=s3.Bucket(bucket)
    image=bucket.Object(key)
    image_data=image.get().get('Body').read()
    # return Image.open(io.BytesIO(image_data))
    return image_data


def upload_file_to_s3_using_put_object(file,file_name):
    """
    Uploads file to s3 using put_object function of resource object.
    Same function is available for s3 client object as well.
    put_object function gives us much more options and we can set object access policy, tags, encryption etc
    :return: None
    """
    s3 = boto3.resource("s3")
    bucket_name = "estimateasy"
    # object_name = "sample_using_put_object.txt"
    # file_name = os.path.join(pathlib.Path(__file__).parent.resolve(), "sample_file.txt")

    bucket = s3.Bucket(bucket_name)
    response = bucket.put_object(
        # ACL="private",
        Body=file,
        # ServerSideEncryption="AES256",
        Key=file_name,
        # Metadata={"env": "dev", "owner": "binary guy"},
    )
    print(
        response
    )  # prints s3.Object(bucket_name='binary-guy-frompython-2', key='sample_using_put_object.txt')

