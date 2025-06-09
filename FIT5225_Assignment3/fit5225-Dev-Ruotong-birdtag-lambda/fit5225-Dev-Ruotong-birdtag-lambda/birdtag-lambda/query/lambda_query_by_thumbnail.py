import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get("TABLE_NAME", "BirdMedia"))

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        thumb_url = body.get("thumbnail_url", "").strip()

        if not thumb_url:
            raise ValueError("Missing 'thumbnail_url' field")

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Invalid request: {str(e)}"})
        }

    try:
        response = table.scan()
        items = response.get("Items", [])

        for item in items:
            if item.get("thumbnail_url") == thumb_url:
                return {
                    "statusCode": 200,
                    "body": json.dumps({"s3_url": item.get("s3_url")})
                }

        return {
            "statusCode": 404,
            "body": json.dumps({"error": "No matching file found"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
