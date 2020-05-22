
import boto3
import os 

import os
location = "us-east-1"
os.environ['AWS_PROFILE'] = "Profile1"
os.environ['AWS_DEFAULT_REGION'] = location

s3 = boto3.client('s3')
response = s3.list_buckets()


bucket_name = "ppriyankbucketdemo"
file_name = "1.jpg"
s3.create_bucket(Bucket=bucket_name)

s3.upload_file(
    file_name, bucket_name, file_name,
    ExtraArgs={'Metadata': {'label': str(1)}}
)

s3_result =  s3.list_objects_v2(Bucket=bucket_name, Delimiter = "/")
if 'Contents' not in s3_result and 'CommonPrefixes' not in s3_result:
        "empty bucket"


files = []
if s3_result.get('Contents'):
        for key in s3_result['Contents']:
            files.append(key['Key'])

metadata = s3.head_object(Bucket=bucket_name, Key=file_name)
metadata["Metadata"]["label"]


for (tag,value) in Image.open("chikka.jpg")._getexif().iteritems():
        print ('%s = %s' % (TAGS.get(tag), value))

with open("chikka.jpg", 'wb') as f:
    s3.download_fileobj(bucket_name, file_name, f)

