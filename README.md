# DIPLOMA APPLICATION

For use this application you can try this:

Just clone this repository 
https://github.com/Vasiliy77745/diploma.git  on your computer

##LOCAL RUNNING

This application listen :5000 port on localhost

Run diploma-app.py script from this repository 

you also need AWS credentials:

    aws_access_key_id
    aws_secret_access_key
    and S3 storage


Export to env your bucket name:
    export AWS_S3_BUCKET="your bucket name"
    
Try check application and upload/get or delete file by username using next endpoints:

####check:
    
    curl 127.0.0.1:5000/healthcheck
####upload:

    curl -F username=testuser -F picture=@test.jpg 127.0.0.1:5000/create
    
####get and show:

    curl -o download.jpg 127.0.0.1:5000/get/testuser
    xdg-open download.jpg
####delete:

    curl -F username=testuser 127.0.0.1:5000/delete
    
###DOCKER

 You also can try to run this app in docker container locally
 
 Build docker image using Dockerfile
 
 Run image with you credentials e.g.
 
    docker build -t imageName .
    docker run -d -e AWS_S3_BUCKET=bucketName -e AWS_ACCESS_KEY_ID=aws_access_key_id -e AWS_SECRET_ACCESS_KEY=aws_secret_access_key --restart always -p 9090:5000 imageName

    Use previous commands for using application

##RUNNING ON A EC2 INSTANCE
###CLOUDFORMATION
There is a ability running this app from a stack on AWS services

This repo included the file stack.yaml

Run this stack with:

    aws cloudformation create-stack --stack-name myapp-dev --region us-east-1 --template-body file://stack.yaml --capabilities CAPABILITY_NAMED_IAM
    
###JENKINS
I also added Jenkinsfiles in this repo for automatically build and deploy  application

Simply make two different jobs on Jenkins using CI and CD Jenkinsfiles

That allow deploy application by commit in Github 
