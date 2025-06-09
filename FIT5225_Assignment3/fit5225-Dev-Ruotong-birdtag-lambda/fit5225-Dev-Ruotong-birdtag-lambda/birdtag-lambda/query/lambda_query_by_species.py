import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get("TABLE_NAME", "BirdMedia"))

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        query_species = body.get("tags", [])

        if not isinstance(query_species, list):
            raise ValueError("Invalid 'tags' format. Expected a list of species names.")

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Invalid request format: {str(e)}"})
        }

    try:
        response = table.scan()
        all_items = response.get("Items", [])

        matching_items = []
        for item in all_items:
            item_tags = item.get("tags", {})
            if any(tag in item_tags for tag in query_species):
                matching_items.append(item)

        results = []
        for item in matching_items:
            url = item.get('thumbnail_url') if item.get('type') == 'image' and 'thumbnail_url' in item else item.get('s3_url')
            results.append({
                "url": url,
                "type": item.get("type", "unknown")
            })

        return {
            "statusCode": 200,
            "body": json.dumps({"results": results})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
