def handler(event, context):
    for record in event.get('Records', []):
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print(f"New object detected: s3://{bucket}/{key}")
    return {"statusCode": 200}
