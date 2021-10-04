import hashlib
import os
import io
import logging
import json
from flask import Flask, request, make_response
import boto3
import botocore

APP = Flask(__name__)
BUCKET = os.environ['AWS_S3_BUCKET']
S3 = boto3.client('s3')
ALLOWED_TYPES = ['image/jpeg', 'image/x-png', 'image/png', 'image/gif']
SIZE_LIMIT = 5 * 1024 * 1024

def get_file_name_by_username(username: str) -> str:
    return hashlib.md5(username.encode()).hexdigest()

@APP.route('/create', methods=['POST'])
def create():
    mime_type = request.files.get('picture').content_type
    file_size = request.files.get('picture').content_length
    if mime_type not in ALLOWED_TYPES:
        return json.dumps({'status': 'error', 'message': 'Wrong image type'}), 500
    if file_size > SIZE_LIMIT:
        return json.dumps({'status': 'error', 'message': 'Picture size too large'}), 500
    try:
        S3.upload_fileobj(
            Fileobj=request.files.get('picture'),
            Bucket=BUCKET,
            Key=get_file_name_by_username(request.form['username']),
            ExtraArgs={
                "ContentType": mime_type
            }
        )
    except botocore.exceptions.ClientError as err:
        logging.error(err)
        return json.dumps({'status': 'error', 'message': 'Upload error'}), 500
    return json.dumps({'status': 'ok', 'message': 'Picture uploaded to S3 bucket'})

@APP.route('/get/<username>', methods=['GET'])
def get(username):
    try:
        picture = S3.get_object(
            Bucket=BUCKET,
            Key=get_file_name_by_username(username)
        )
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == 'NoSuchKey':
            return json.dumps({'status': 'error', 'message':'Username not found'}), 404
        logging.error(err)
        return json.dumps({'status': 'error', 'message':'File get error'}), 500
    else:
        content = picture['Body'].read()
        response = make_response(content)
        mime_type = picture['ResponseMetadata']['HTTPHeaders']['content-type']
        response.headers.set('Content-Type', mime_type)
        response.headers.set('Content-Length', len(content))
        return response

@APP.route('/delete', methods=['POST'])
def delete():
    try:
        S3.head_object(
            Bucket=BUCKET,
            Key=get_file_name_by_username(request.form['username'])
        )
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == '404':
            return json.dumps({'status': 'error', 'message': 'Username not found'}), 404
        logging.error(err)
        return json.dumps({'status': 'error', 'message': 'Picture deleting error'}), 500
    else:
        S3.delete_object(
            Bucket=BUCKET,
            Key=get_file_name_by_username(request.form['username'])
        )
        return json.dumps({'status': 'ok', 'message': 'Picture deleted'})

@APP.route('/healthcheck', methods=['GET'])
def healthcheck():
    try:
        S3.upload_fileobj(
            Fileobj=io.BytesIO(str.encode('testfile')),
            Bucket=BUCKET,
            Key='testfile'
        )
    except botocore.exceptions.ClientError as err:
        logging.error(err)
        return json.dumps({'status':'error'}), 500
    else:
        return json.dumps({'status':'ok'})


if __name__ == '__main__':
    APP.run(debug=True)
