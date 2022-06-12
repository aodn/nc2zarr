import boto3

import crhelper

LOGGER = crhelper.log_config({"RequestId": "CONTAINER_INIT"})
LOGGER.info('Logging configured')


def empty_bucket(bucket_name):
    bucket = boto3.resource('s3').Bucket(bucket_name)

    if not any(l for l in bucket.Tagging().tag_set if l['Key'] == 'Bucket' and l['Value'] == bucket_name):
        raise ValueError("bucket '{bucket}' does not have expected tag. Not deleting!".format(bucket=bucket))

    LOGGER.info("emptying bucket {bucket_name}".format(bucket_name=bucket_name))
    bucket.objects.all().delete()


#
# Event functions - custom code executed when the corresponding event is received from the stack
#

def create(event, context):
    return 'EmptyBucketPhysicalResourceId', {}


def update(event, context):
    return 'EmptyBucketPhysicalResourceId', {}


def delete(event, context):
    bucket_name = event['ResourceProperties']['BucketName']
    empty_bucket(bucket_name)


#
# Lambda entry point
#

def handler(event, context):
    global LOGGER
    LOGGER = crhelper.log_config(event)
    return crhelper.cfn_handler(event, context, create, update, delete, LOGGER, init_failed=False)
