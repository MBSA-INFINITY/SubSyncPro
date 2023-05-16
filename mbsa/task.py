from celery import shared_task
from time import sleep
from firebase import Firebase
from .models import  TemporaryFile
import boto3
from .helper import *

firebaseConfig = {
  "apiKey": "AIzaSyD6vjqgRXjs4cs1OTghrqxcgtG-jdg-OdQ",
  "authDomain": "fir-flask-app-ba8ce.firebaseapp.com",
  "databaseURL": "https://fir-flask-app-ba8ce-default-rtdb.firebaseio.com",
  "projectId": "fir-flask-app-ba8ce",
  "storageBucket": "fir-flask-app-ba8ce.appspot.com",
  "messagingSenderId": "741872754982",
  "appId": "1:741872754982:web:7c51caf1593b8821d7e1e7",
  "measurementId": "G-EFVXY2L9G6"
}
firebase = Firebase(firebaseConfig)
db = firebase.database()

s3 = boto3.resource(
    service_name='s3',
    aws_access_key_id='AKIAWGU44PD7MGWRXM65',
    aws_secret_access_key="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"
)
S3_BUCKET_NAME = "ecowiser"

bucket = s3.Bucket(S3_BUCKET_NAME)


@shared_task
def sleepy(duration):
    sleep(duration)
    return None


@shared_task
def update_key(key):
    sleep(5)
    db.child("all_keys").child(key).set(True)
    return None


@shared_task
def upload_to_s3(image_upload_id, object_key,file_ext):
    my_uploaded_file = TemporaryFile.objects.get(id=image_upload_id)
    # print(my_uploaded_file)
    bucket.upload_fileobj(my_uploaded_file.file, object_key ,ExtraArgs={'ContentType': f'video/{file_ext}'})
    object_acl = s3.ObjectAcl(S3_BUCKET_NAME, object_key)
    object_acl.put(ACL='public-read')
    # os.remove(f"static/{object_key}.mp4")
    db.child("all_keys").child(object_key).update({"uploaded_s3":True,"video_link":f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{object_key}"})
    return None


@shared_task
def upload_to_dynamodb(image_upload_id, object_key, file_ext):
    my_uploaded_file = TemporaryFile.objects.get(id=image_upload_id)
    handle_uploaded_file(my_uploaded_file.file,f"static/{object_key}.{file_ext}")
    extract_subtitles(f"static/{object_key}.{file_ext}",f"static/{object_key}.txt")
    all_subtitles = parse_subtitle_file(f"static/{object_key}.txt")
    if all_subtitles:
        upload_sub_to_dynamo(all_subtitles, object_key)
        db.child("all_keys").child(object_key).update({"uploaded_dynamodb":True,"subtitles": True})
    else:
        db.child("all_keys").child(object_key).update({"uploaded_dynamodb":True,"subtitles": False})
    return None
