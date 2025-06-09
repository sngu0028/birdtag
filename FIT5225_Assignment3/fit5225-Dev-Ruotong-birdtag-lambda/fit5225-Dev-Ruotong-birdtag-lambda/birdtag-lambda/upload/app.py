# app.py
import json
import boto3
import os

os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"
os.environ["ULTRALYTICS_REQUIREMENTS_AUTO_INSTALL"] = "False"


from create_thumbnail_from_s3 import create_thumbnail_from_s3
from image_handler import process_image
# from audio_handler import process_audio
from video_handler import process_video

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get("TABLE_NAME", "BirdMedia"))
s3_client = boto3.client('s3')

def save_metadata_to_dynamodb(s3_url, file_type, tags_dict, thumbnail_url=None, source_model="default"):
    import uuid
    from datetime import datetime

    id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    item = {
        'id': id,
        'type': file_type,
        's3_url': s3_url,
        'tags': tags_dict,
        'timestamp': timestamp,
        'source_model': source_model
    }

    if thumbnail_url:
        item['thumbnail_url'] = thumbnail_url

    table.put_item(Item=item)
    print("Item saved:", item)

def lambda_handler(event, context):
    try:
        s3_bucket = event['Records'][0]['s3']['bucket']['name']
        s3_key = event['Records'][0]['s3']['object']['key']
        print(f"File uploaded: {s3_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error parsing S3 event: {e}")
        return {"statusCode": 400, "body": "Bad S3 event"}

    s3_url = f"https://{s3_bucket}.s3.amazonaws.com/{s3_key}"

    if s3_key.endswith(('.jpg', '.jpeg', '.png')):
        return process_image(s3_bucket, s3_key, s3_url, save_metadata_to_dynamodb)
    # elif s3_key.endswith(('.wav', '.mp3')):
    #     return process_audio(s3_bucket, s3_key, s3_url, save_metadata_to_dynamodb)
    elif s3_key.endswith(('.mp4', '.mov')):
        return process_video(s3_bucket, s3_key, s3_url, save_metadata_to_dynamodb)
    else:
        return {"statusCode": 400, "body": "Unsupported file type"}
