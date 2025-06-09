import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get("TABLE_NAME", "BirdMedia"))

def parse_tags(tag_list):
    parsed = {}
    for entry in tag_list:
        try:
            name, count = entry.split(",")
            parsed[name.strip()] = int(count)
        except:
            continue
    return parsed

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        urls = body.get("url", [])
        op = int(body.get("operation", -1))
        raw_tags = body.get("tags", [])

        if op not in [0, 1]:
            raise ValueError("Invalid operation (must be 0 or 1)")

        tags = parse_tags(raw_tags)
        if not tags or not urls:
            raise ValueError("Missing tags or urls")

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Invalid input: {str(e)}"})
        }

    updated = []
    for url in urls:
        try:
            # 查找对应项
            response = table.scan()
            target_item = None
            for item in response.get("Items", []):
                if item.get("thumbnail_url") == url or item.get("s3_url") == url:
                    target_item = item
                    break

            if not target_item:
                continue

            item_id = target_item["id"]
            current_tags = target_item.get("tags", {})

            if op == 1:  # 添加
                for k, v in tags.items():
                    current_tags[k] = current_tags.get(k, 0) + v
            elif op == 0:  # 删除
                for k in tags:
                    if k in current_tags:
                        del current_tags[k]

            # 更新数据库
            table.update_item(
                Key={"id": item_id},
                UpdateExpression="SET tags = :t",
                ExpressionAttributeValues={":t": current_tags}
            )
            updated.append(url)

        except Exception as e:
            print(f"Failed to update {url}: {e}")
            continue

    return {
        "statusCode": 200,
        "body": json.dumps({
            "updated": updated,
            "operation": "add" if op == 1 else "remove"
        })
    }
