# SubSyncPro

## Description

 SubSyncPro is a portal that allows users to upload videos, extracts the subtitles from the uploaded videos using the ccextractor tool and search for the exact timestamp for a particular keyword in the video. The extracted subtitles are saved into AWS DynamoDB, and the processed video is stored in AWS S3. The project is built using Django and utilizes Redis and Celery for queuing and processing tasks.

## Features

- Automatic subtitle extraction using ccextractor
- Efficient task management with Redis and Celery
- Seamless integration with AWS S3 for video storage
- Subtitle storage and retrieval using DynamoDB
- Querying the user keywords for timestamp extraction

## Installation

1. Clone the repository:

   ```python
   git clone git@github.com:MBSA-INFINITY/SubSyncPro.git
   cd SubSyncPro
   ```
2. Create a virtual environment and activate it:
   ```shell
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required dependencies::
   ```shell
    pip install -r requirements.txt
   ```
4. Set up the database:
   ```shell 
   python manage.py migrate
   ```
5. Configure AWS S3 and DynamoDB:
   - Create an AWS account if you don't have one.
   - Create an S3 bucket to store the processed videos.
   - Get the aws_access_key_id, aws_access_key_secret from the AWS Dashboard.
   - Put the credentials at the required places in the code.

6. Configure Redis: 
    - Install Redis if not already installed.
    - Start Redis server on your local machine or use a remote Redis server.
    -  Update the Redis configuration in settings.py with the appropriate host, port, and password(if required).

7. Start the Celery worker:
   ```shell
   celery -A ecowiser worker -l info -P eventlet
   ```

