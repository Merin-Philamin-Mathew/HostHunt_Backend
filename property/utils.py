
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 6 
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_page_size(self, request):
        if hasattr(self, 'custom_page_size'):
            return self.custom_page_size
        return super().get_page_size(request)

import boto3
import urllib.parse
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status 

region_name = settings.AWS_S3_REGION_NAME
bucket_name = settings.AWS_STORAGE_BUCKET_NAME
s3_url_prefix = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/"

s3 = boto3.client('s3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=region_name)

def get_s3_file_url(file_name, s3_file_path):

    encoded_file_name = urllib.parse.quote(file_name)

    file_url = s3_url_prefix+s3_file_path+encoded_file_name
    print('image_url', file_url)

    return file_url



def Upload_to_s3(image_file,s3_file_path):
    try:
        s3.upload_fileobj(image_file, bucket_name, s3_file_path+image_file.name,
                        ExtraArgs={ 'ContentType': image_file.content_type})
        image_url = get_s3_file_url(image_file.name,s3_file_path)
        return image_url
    except Exception as e:
        print('3 error',e)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def download_file_from_s3(s3_file_path):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=s3_file_path)
        file_content = response['Body'].read()
        return file_content
    except Exception as e:
        print('Error while fetching the file:', e)
        return None
    

def delete_file_from_s3(s3_file_path,file_name):
    try:
        s3_file_path+urllib.parse.quote(file_name)
        s3.delete_object(Bucket=bucket_name, Key=s3_file_path)
        print(f"{s3_file_path} deleted successfully from {bucket_name}")
        return True
    except Exception as e:
        print('Error while deleting the file:', e)
        return False
    
def extract_s3_key_from_url(url):
    if url.startswith(s3_url_prefix):
        file_key = url[len(s3_url_prefix):]
        
        decoded_key = urllib.parse.unquote(file_key)
        return decoded_key
    else:
        raise ValueError("Invalid S3 URL or mismatch with bucket/region")
    
def delete_file_from_s3_by_url(url):
    try:
        s3_file_path = extract_s3_key_from_url(url)
        s3.delete_object(Bucket=bucket_name, Key=s3_file_path)
        print(f"{s3_file_path} deleted successfully from {bucket_name}")
        return True
    except Exception as e:
        print('Error while deleting the file:', e)
        return False

