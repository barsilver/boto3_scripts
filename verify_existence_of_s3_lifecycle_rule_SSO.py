import boto3

s3 = boto3.resource('s3')
session = boto3.session.Session(profile_name='pai-non-prod')
s3_client = session.client('s3')
list_buckets = s3_client.list_buckets()
buckets = list_buckets["Buckets"]

for bucket in buckets:
    bucket = bucket["Name"]
    try:
      data = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket)
      rules = data.get('Rules')
      if any(d['ID'] == 'S3_storageClass' for d in rules):
        rules = "Policy Exists"
    except:
      rules = 'No Policy'

    print(bucket, rules)
