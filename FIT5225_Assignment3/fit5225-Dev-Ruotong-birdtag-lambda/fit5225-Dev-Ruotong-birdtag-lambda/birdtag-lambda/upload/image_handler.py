# image_handler.py
import os
import numpy as np
from create_thumbnail_from_s3 import create_thumbnail_from_s3

model = None 
model_local_path = "models/model.pt"

def download_yolo_model():
    if not os.path.exists(model_local_path):
        raise FileNotFoundError("model.pt not found in models/ folder")
    return model_local_path

def process_image(s3_bucket, s3_key, s3_url, save_fn, save_metadata_to_dynamodb=None, local_mode=False):
    global model  
    print(f"Starting image processing for {s3_key}...")

    try:
        if local_mode:
            local_path = s3_key
        else:
            import boto3
            s3 = boto3.client('s3')
            local_path = f"/tmp/{os.path.basename(s3_key)}"
            s3.download_file(s3_bucket, s3_key, local_path)

        if model is None:
            model_path = download_yolo_model()
            from ultralytics import YOLO
            model = YOLO(model_path)

            import cv2
            dummy_image_path = "/tmp/dummy.jpg"
            black_img = np.zeros((640, 640, 3), dtype=np.uint8)
            cv2.imwrite(dummy_image_path, black_img)

            model.predict(source=dummy_image_path, imgsz=640, verbose=False)


        result = model(local_path)[0]
        labels = result.boxes.cls.tolist()

        tag_count = {}
        for label in labels:
            name = model.names[int(label)]
            tag_count[name] = tag_count.get(name, 0) + 1

        thumbnail_url = create_thumbnail_from_s3(s3_bucket, s3_key, None, local_mode=False)

        if save_fn:
            save_fn(s3_url, "image", tag_count, thumbnail_url, source_model="image-model-v1")

        return tag_count

    except Exception as e:
        print(f"Image processing error: {e}")
        return {"statusCode": 500, "body": "Image processing failed"}