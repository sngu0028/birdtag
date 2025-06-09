# lambda_query_by_file
import os
import json
import boto3
from audio_handler import process_audio
from image_handler import process_image
from video_handler import process_video

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get("TABLE_NAME", "BirdMedia"))
s3_client = boto3.client('s3')

def find_similar_items(query_tags):
    response = table.scan()
    items = response.get("Items", [])
    results = []

    for item in items:
        item_tags = item.get("tags", {})
        try:
            matched = all(
                float(item_tags.get(tag, 0)) >= float(count)
                for tag, count in query_tags.items()
            )
        except Exception:
            matched = False

        if matched:
            url = item.get("thumbnail_url") if item["type"] == "image" and "thumbnail_url" in item else item["s3_url"]
            results.append({
                "url": url,
                "type": item.get("type", "unknown")
            })

    return results

def lambda_handler(event, context):
    try:
        s3_bucket = event['Records'][0]['s3']['bucket']['name']
        s3_key = event['Records'][0]['s3']['object']['key']
        print(f"Query-file uploaded: {s3_bucket}/{s3_key}")

        s3_url = f"https://{s3_bucket}.s3.amazonaws.com/{s3_key}"

        if s3_key.endswith(('.jpg', '.jpeg', '.png')):
            tags = process_image(s3_bucket, s3_key, s3_url, save_fn=None)
        elif s3_key.endswith(('.wav', '.mp3')):
            tags = process_audio(s3_bucket, s3_key, s3_url, save_fn=None)
        elif s3_key.endswith(('.mp4', '.mov')):
            tags = process_video(s3_bucket, s3_key, s3_url, save_fn=None)
        else:
            return {"statusCode": 400, "body": json.dumps({"error": "Unsupported file type"})}

        if not isinstance(tags, dict):
            return {"statusCode": 500, "body": json.dumps({"error": "Failed to extract tags"})}

        matching_results = find_similar_items(tags)

        return {
            "statusCode": 200,
            "body": json.dumps({"query_tags": tags, "results": matching_results})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
