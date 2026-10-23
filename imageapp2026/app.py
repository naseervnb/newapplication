import io
from flask import Flask, request
from PIL import Image
import boto3

# Inside your image upload/compress route:
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # 1. Read file bytes into memory once so it can be reused safely
    file_bytes = file.read()

    # 2. Upload original file to S3
    s3 = boto3.client('s3')
    s3.upload_fileobj(io.BytesIO(file_bytes), 'YOUR_S3_BUCKET_NAME', file.filename)

    # 3. Open image with Pillow using a fresh stream
    image = Image.open(io.BytesIO(file_bytes))
    
    # ... perform your compression and save/return logic here ...
    
    return "Image processed, backed up to S3, and SMS sent successfully!"