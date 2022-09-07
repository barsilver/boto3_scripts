# Edit PROFILE_NAME, STRING, FILE  before running the script.

import boto3

strings = ['<STRING>']
source_file = "<FILE>"

lines = []
with open(source_file) as file:
    for line in file:
        if not any(string in line for string in strings):
            lines.append(line.split(" ", 1)[0])

lifecycle_configuration = {
    "Rules": [{"ID": "S3_storageClass",
               "Filter": {},
               "Status": "Enabled",
               "Transitions": [{"Days": 0, "StorageClass": "INTELLIGENT_TIERING"}],
               "NoncurrentVersionTransitions": [{"NoncurrentDays": 0,
                                                 "StorageClass": "INTELLIGENT_TIERING"}]
               }]
}


session = boto3.session.Session(profile_name='<PROFILE_NAME>')  # profile defined in ~/.aws/credentials
s3 = boto3.resource('s3')

for bucket in lines:
    message = 'INTELLIGENT_TIERING rule added'
    s3_client = session.client('s3')
    s3_client.put_bucket_lifecycle_configuration(Bucket=bucket, LifecycleConfiguration=lifecycle_configuration)
    print(bucket, message)
