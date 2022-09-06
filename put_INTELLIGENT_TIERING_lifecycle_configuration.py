# Edit PROFILE_NAME before running the script.

import boto3

lifecycle_configuration = {
    "Rules": [{"ID": "S3_storageClass",
               "Filter": {},
               "Status": "Enabled",
               "Transitions": [{"Days": 0, "StorageClass": "INTELLIGENT_TIERING"}],
               "NoncurrentVersionTransitions": [{"NoncurrentDays": 0,
                                                 "StorageClass": "INTELLIGENT_TIERING"}]
               }]
session = boto3.session.Session(profile_name=<PROFILE_NAME>)  # profile defined in ~/.aws/credentials

for bucket in s3.buckets.all():
    try:
        rules = bucket.Lifecycle().rules
    except:
        rules = 'INTELLIGENT_TIERING rule added'
        s3_client = session.client("s3")
        s3_client.put_bucket_lifecycle_configuration(Bucket=bucket, LifecycleConfiguration=lifecycle_configuration)
    print(bucket.name, rules)
