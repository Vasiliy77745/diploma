from flask import Flask, request, make_response
import boto3, botocore
import hashlib
import gzip
import os
import logging

app = Flask(__name__)
bucket = os.environ['AWS_S3_BUCKET']
s3 = boto3.client('s3')
allowedTypes = ['image/jpeg', 'image/x-png', 'image/png', 'image/gif']
sizeLimit = 3 * 1024 * 1124

def getFilenameByUsername(username: str) -> str:
    return(hashlib.md5(username.encode()).hexdigest())


@app.route('/')
def index():
  return '''<h1>Upload a profile picture</h1>
  <form method=POST enctype=multipart/form-data action="create">
  <input type=text name=username>
  <input type=file name=picture>
  <input type=submit>
  </form>
  <br>
  <h1>Get picture by username</h1>
  <form method=POST enctype=multipart/form-data action="get">
  <input type=text name=username>
  <input type=submit>
  </form>
  <br>
  <h1>Delete picture by username</h1>
  <form method=POST enctype=multipart/form-data action="delete">
  <input type=text name=username>
  <input type=submit>
  </form>'''

@app.route('/create', methods=['POST'])
def create():
  mimeType = request.files.get('picture').content_type
  fileSize = request.files.get('picture').content_length
  if mimeType not in allowedTypes:
    return f'<h2>Wrong image type</h2><h3>See allowed types of images</h3><li>{allowedTypes}</li>', 500
  if fileSize > sizeLimit:
    return 'Picture size too large', 500
  try:
    s3.upload_fileobj(
      Fileobj = request.files.get('picture'), 
      Bucket = bucket, 
      Key = getFilenameByUsername(request.form['username']),
      ExtraArgs={
        "ContentType": mimeType
      }
    )
  except botocore.exceptions.ClientError as e:
    logging.error(e)
    return "Upload error", 500
  return f"Picture uploaded to s3 bucket storage with name {bucket}"
    
@app.route('/get', methods=['POST'])
def get():
  try:
    picture = s3.get_object(
      Bucket = bucket, 
      Key = getFilenameByUsername(request.form['username'])
    )
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == 'NoSuchKey':
      return 'Username not found', 404
    else:
      logging.error(e)
      return 'File get error', 500
  else:
    content = gzip.compress((picture['Body'].read()))
    response = make_response(content)
    response.headers.set('Content-Type', picture['ResponseMetadata']['HTTPHeaders']['content-type'])
    response.headers.set('Content-Length', len(content))
    response.headers['Content-Encoding'] = 'gzip'
    return response

@app.route('/delete', methods=['POST'])
def delete():
  try:
    s3.head_object(
      Bucket = bucket, 
      Key = getFilenameByUsername(request.form['username'])
    )
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == '404':
      return 'Username not found', 404
    else:
      logging.error(e)
      return 'Picture deleting error', 500
  else:
    s3.delete_object(
      Bucket = bucket, 
      Key = getFilenameByUsername(request.form['username'])
    )
    return 'Picture deleted'
      
@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return('OK')


if __name__ == '__main__':
    app.run(debug=True)
