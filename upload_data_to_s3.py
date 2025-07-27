import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

BUCKET = os.environ.get('S3_BUCKET', 'ml-crash-course-data')
KEY = os.environ.get('S3_KEY', 'House_Rent_Dataset.csv')
LOCAL_PATH = os.environ.get('LOCAL_PATH', 'data/House_Rent_Dataset.csv')
ENDPOINT_URL = os.environ.get('S3_ENDPOINT_URL')  # For MinIO/local

session = boto3.session.Session()
s3 = session.client('s3', endpoint_url=ENDPOINT_URL)

def ensure_bucket_exists(bucket):
    try:
        s3.head_bucket(Bucket=bucket)
        print(f"Bucket {bucket} already exists.")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Bucket {bucket} does not exist. Creating...")
            try:
                s3.create_bucket(Bucket=bucket)
                print(f"Bucket {bucket} created successfully.")
            except ClientError as create_error:
                print(f"Error creating bucket: {create_error}")
                raise
        elif e.response['Error']['Code'] == '403':
            print(f"Access denied to bucket {bucket}. Trying to upload anyway...")
        else:
            print(f"Error checking bucket: {e}")
            raise

def file_exists(bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        elif e.response['Error']['Code'] == '403':
            print(f"Access denied checking file existence. Assuming it doesn't exist.")
            return False
        raise

def upload_file():
    try:
        if not file_exists(BUCKET, KEY):
            print(f'Uploading {LOCAL_PATH} to s3://{BUCKET}/{KEY}')
            s3.upload_file(LOCAL_PATH, BUCKET, KEY)
            print('Upload complete.')
        else:
            print(f's3://{BUCKET}/{KEY} already exists. Skipping upload.')
    except NoCredentialsError:
        print("No AWS credentials found. Please check your credentials.")
    except ClientError as e:
        print(f"Error during upload: {e}")
        if e.response['Error']['Code'] == '403':
            print("Access denied. Please check your credentials and permissions.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == '__main__':
    upload_file() 