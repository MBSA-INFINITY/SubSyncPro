import subprocess
import os
import re
from itertools import groupby
from collections import namedtuple
import boto3
from boto3.dynamodb.conditions import Attr

db = boto3.resource(
    service_name='dynamodb',
    aws_access_key_id='AKIAWGU44PD7MGWRXM65',
    aws_secret_access_key="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",
    region_name='us-west-1'
)
__TableName__ = "ecowiser"
table = db.Table(__TableName__)

Subtitle = namedtuple('Subtitle', 'number start end content')


def extract_subtitles(video_path, output_path):
    # Run CCExtractor command using subprocess
    command = ["ccextractor", video_path, "-o", output_path]
    subprocess.run(command)

    # Check if the output subtitle file was created
    if os.path.isfile(output_path):
        print("Subtitles extracted successfully!")
    else:
        print("Subtitles extraction failed.")

def handle_uploaded_file(f, filename):
    with open(filename, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def parse_subtitle_file(filename):
    with open(filename,'r',errors='ignore',encoding='utf-8') as f:
        res = [list(g) for b,g in groupby(f, lambda x: bool(x.strip())) if b]
    subs = []
    for sub in res:
        if len(sub) >= 3: # not strictly necessary, but better safe than sorry
            sub = [x.strip() for x in sub]
            number, start_end, *content = sub # py3 syntax
            start, end = start_end.split(' --> ')
            subs.append(list(Subtitle(re.sub(r'\W+', '', number), start, end, re.sub(r'\W+', ' ', " ".join(content)).lower())))
    return subs

def upload_sub_to_dynamo(all_subtitles,object_key):
    if all_subtitles:
        all_subtitles_json = []
        for subtitle in all_subtitles:
            all_subtitles_json.append({
            "sno":subtitle[0],
            "start":subtitle[1],
            "end":subtitle[2],
            "content":subtitle[3],
            "object_key":object_key
            })
        with table.batch_writer() as batch:
            for item in all_subtitles_json:
                response = batch.put_item(Item={
                    "sno":item["sno"],
                    "start":item["start"],
                    "end":item["end"],
                    "content":item["content"],
                    "object_key":item["object_key"]
                })
            
def search_subtitles(search_query):
    search_query = search_query.lower()
    response = table.scan(
        FilterExpression=Attr('content').contains(search_query)
  )
    return response['Items']
        
    
