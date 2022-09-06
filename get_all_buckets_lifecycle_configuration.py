#!/Users/bar.silver/.pyenv/shims/python3

import boto3


s3 = boto3.resource('s3')

for bucket in s3.buckets.all():
    try:
        rules = bucket.Lifecycle().rules
    except:
        rules = 'No Policy'
    print(bucket.name, rules)
