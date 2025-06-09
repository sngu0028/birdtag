import cv2
import os
import numpy as np


def create_thumbnail_from_s3(bucket_name, image_key, thumbnail_key, local_mode=False):
    if local_mode:
        print("Skipping S3 thumbnail creation in local mode.")
        return "https://fake-thumbnail.url/from-local-mode"
    
    if thumbnail_key is None:
        thumbnail_key = f"thumbnails/thumb_{os.path.basename(image_key)}"

    download_path = f"/tmp/{os.path.basename(image_key)}"

    import boto3
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, image_key, download_path)
    local_filename = "/tmp/image.jpg"
    thumbnail_filename = "/tmp/thumbnail.jpg"

    image = cv2.imread(download_path)
    if image is None:
        raise ValueError("Could not read image with OpenCV.")

    height, width = image.shape[:2]
    new_width = 200
    new_height = int((new_width / width) * height)
    thumbnail = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    thumbnail_path = f"/tmp/thumb_{os.path.basename(image_key)}"
    cv2.imwrite(thumbnail_path, thumbnail)

    s3.upload_file(thumbnail_path, bucket_name, thumbnail_key)

    return f"https://{bucket_name}.s3.amazonaws.com/{thumbnail_key}"