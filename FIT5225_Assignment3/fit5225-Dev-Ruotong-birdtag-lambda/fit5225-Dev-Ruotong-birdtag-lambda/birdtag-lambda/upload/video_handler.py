# video_handler.py
import os
import cv2

model = None  
model_local_path = "models/model.pt"

def download_yolo_model():
    if not os.path.exists(model_local_path):
        raise FileNotFoundError("model.pt not found in models/ folder")
    return model_local_path

def process_video(s3_bucket, s3_key, s3_url, save_fn, local_mode=False):
    global model
    try:
        if local_mode:
            local_path = s3_key
        else:
            import boto3
            s3_client = boto3.client('s3')
            local_path = f"/tmp/{os.path.basename(s3_key)}"
            s3_client.download_file(s3_bucket, s3_key, local_path)

        if model is None:
            model_path = download_yolo_model()
            from ultralytics import YOLO
            model = YOLO(model_path)

        cap = cv2.VideoCapture(local_path)

        frame_count = 0
        tag_count = {}

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            if frame_count % 10 != 0:
                continue
            frame_path = f"/tmp/frame_{frame_count}.jpg"
            cv2.imwrite(frame_path, frame)
            results = model(frame_path)[0]
            labels = results.boxes.cls.tolist()
            for label in labels:
                name = model.names[int(label)]
                tag_count[name] = tag_count.get(name, 0) + 1

        cap.release()

        save_fn(s3_url, "video", tag_count, source_model="image-model-v1")
        return tag_count

    except Exception as e:
        print(f"Video processing error: {e}")
        return {"statusCode": 500, "body": "Video processing failed"}