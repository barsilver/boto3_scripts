import boto3


s3 = boto3.resource('s3')
buckets = s3.buckets.all() # or buckects list as you wish

for bucket in buckets:
    try:
    # if using buckets list and not s3.buckets.all()
    #bucket = s3.Bucket(bucket)
        rules = bucket.Lifecycle().rules
        if any(d['ID'] == '<RULE_ID>' for d in rules):
          rules = "Policy Exists"
    except:
        rules = 'No Policy'
    print(bucket.name, rules)
