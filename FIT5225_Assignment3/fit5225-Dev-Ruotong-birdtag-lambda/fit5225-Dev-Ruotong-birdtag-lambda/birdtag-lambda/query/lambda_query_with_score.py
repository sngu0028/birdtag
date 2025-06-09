import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get("TABLE_NAME", "BirdMedia"))

def find_similar_items_with_score(query_tags):
    response = table.scan()
    items = response.get("Items", [])
    results = []

    for item in items:
        item_tags = item.get("tags", {})
        match_count = 0
        total_query_tags = len(query_tags)
        matched_list = []

        for tag, q_count in query_tags.items():
            try:
                if float(item_tags.get(tag, 0)) >= float(q_count):
                    match_count += 1
                    matched_list.append(tag)
            except Exception:
                continue

        if match_count > 0:
            url = item.get("thumbnail_url") if item.get("type") == "image" and "thumbnail_url" in item else item.get("s3_url")
            match_ratio = round(match_count / total_query_tags, 2)

            results.append({
                "url": url,
                "type": item.get("type", "unknown"),
                "matched_tags": match_count,
                "total_tags": total_query_tags,
                "match_ratio": match_ratio,
                "matched_list": matched_list
            })

    results.sort(key=lambda x: x["match_ratio"], reverse=True)
    return results

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        query_tags = body.get("tags", {})

        if not isinstance(query_tags, dict):
            raise ValueError("Invalid 'tags' format. Must be a JSON object like {'bird': 2}")

        results = find_similar_items_with_score(query_tags)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "query_tags": query_tags,
                "results": results
            })
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }
