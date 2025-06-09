# lambda_delete_files
import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get("TABLE_NAME", "BirdMedia"))
s3_client = boto3.client("s3")
bucket_name = os.environ.get("BUCKET_NAME", "your-s3-bucket-name")

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        urls = body.get("urls", [])

        if not isinstance(urls, list) or not urls:
            raise ValueError("Missing or invalid 'urls' list")

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Invalid input: {str(e)}"})
        }

    deleted = []
    failed = []

    # 查找匹配项
    try:
        response = table.scan()
        all_items = response.get("Items", [])

        for url in urls:
            matched = None
            for item in all_items:
                if item.get("s3_url") == url or item.get("thumbnail_url") == url:
                    matched = item
                    break

            if not matched:
                failed.append({"url": url, "reason": "Not found in database"})
                continue

            try:
                # 删除原始文件
                s3_key = matched["s3_url"].split(f"{bucket_name}/")[-1]
                s3_client.delete_object(Bucket=bucket_name, Key=s3_key)

                # 如果是图片，删除缩略图
                if matched.get("type") == "image" and matched.get("thumbnail_url"):
                    thumb_key = matched["thumbnail_url"].split(f"{bucket_name}/")[-1]
                    s3_client.delete_object(Bucket=bucket_name, Key=thumb_key)

                # 删除数据库记录
                table.delete_item(Key={"id": matched["id"]})
                deleted.append(url)

            except Exception as e:
                failed.append({"url": url, "reason": str(e)})

        return {
            "statusCode": 200,
            "body": json.dumps({"deleted": deleted, "failed": failed})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
