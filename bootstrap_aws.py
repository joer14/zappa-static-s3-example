#!/usr/bin/env python
import os
import boto3
import botocore
import json
import mimetypes
'''
Setup some aws resources that zappa does not create.
Also includes frontend uploader code.
'''

AWS_REGION = 'us-west-1' # us-east-1 was causing issues. AWS inconsistencies are the best

STAGES = ['dev','staging','production']

FRONTEND_BUCKET_PREFIX='run-fm-party'

def create_frontend_buckets():
    '''
        For each stage, create a bucket and configure it for frontend hosting.
        If the bucket already exists, just configure it.
        #todo - allow me to explictly state which aws credential profile to use
    '''
    STAGES=['reallydev65']
    s3_client = boto3.client('s3')
    for stage in STAGES:
        bucket_name = '{}-{}'.format(FRONTEND_BUCKET_PREFIX,stage)
        # get or create the bucket
        try:
            resp = s3_client.head_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError:
            bucket = s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': AWS_REGION
                },
            )
            resp = s3_client.head_bucket(Bucket=bucket_name)
        # setup s3 to serve static files
        website_configuration = {
            'ErrorDocument': {'Key': 'index.html'},
            'IndexDocument': {'Suffix': 'index.html'},
        }
        s3_client.put_bucket_website(Bucket=bucket_name, WebsiteConfiguration=website_configuration)
        # set bucket policy so files are public by default
        bucket_policy = {
              "Version": "2012-10-17",
              "Statement": [
                {
                  "Action": [
                    "s3:GetObject"
                  ],
                  "Effect": "Allow",
                  "Resource": "arn:aws:s3:::{}/*".format(bucket_name),
                  "Principal": "*"
                }
              ]
        }
        s3_client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))
    return

def configure_apigateway(stage):
    '''
        For each stage, configure api gateway to serve frontend from the root url
        #todo - allow me to explictly state which aws credential profile to use

        - questions
            - can I make the root level / redirect to s3 except /api ???
            - where does cloudfront fit into all of this
            - good guide: https://medium.com/@john.titus/moving-a-simple-api-to-amazon-s-api-gateway-680d025e0921
    '''
    api_gateway_region = 'us-east-2'
    gateway_name = '{}-{}'.format(FRONTEND_BUCKET_PREFIX,stage)
    client = boto3.client('apigateway',api_gateway_region)
    dists = client.get_rest_apis()['items']
    for d in dists:
        # print d
        if d['name'] == gateway_name:
            print d

        dev_rest_api_id = 'p9nxvztsoa'
        '''
        resouces root = /

        '''
    return
    # raise NotImplementedError




















def create_dynamodb_tables():
    '''
        For each stage, create the necessary tables for the app, if they don't
        exist already.
    '''
    raise NotImplementedError

def upload_frontend(stage):
    '''
        For the given stage, empty the bucket, then recursively upload all files
        in /frontend/build to the respective s3 bucket.
        #todo - allow me to explictly state which aws credential profile to use
    '''
    s3_client = boto3.client('s3')
    bucket_name = '{}-{}'.format(FRONTEND_BUCKET_PREFIX,stage)
    # first delete all files in the bucket
    s3 = boto3.resource('s3')
    s3.Bucket(bucket_name).objects.all().delete()
    # specify the frontend build directory
    app_location = os.path.dirname(os.path.abspath(__file__))
    frontend_build_location = os.path.join(app_location,'frontend','build')
    # get a list of all files in directory, recursively.
    paths = [os.path.join(dp, f) for dp, dn, filenames in os.walk(frontend_build_location) for f in filenames]
    for source_path in paths:
        # This isn't windows friendly but whatever - this is my side project.
        dest_path = source_path.split(frontend_build_location)[1].strip('/')
        # boto3 strips the mime type when uploading, so we need to guess it and set it explicitly.
        mime_type, encoding = mimetypes.guess_type(source_path)
        if mime_type is None:
            mime_type = 'binary/octet-stream'
        s3_client.upload_file(source_path, bucket_name, dest_path, ExtraArgs={'ContentDisposition':'inline','ContentType':mime_type})

if __name__ == "__main__":
    # create_frontend_buckets()
    # print create_dynamodb_tables()
    print configure_apigateway('dev')
