import io
import os
from flask import Flask, request, render_template
from PIL import Image
import boto3

app = Flask(__name__)

# Initialize AWS clients
s3_client = boto3.client('s3', region_name='us-east-1')
sns_client = boto3.client('sns', region_name='us-east-1')

# Correct Topic ARN (without the trailing subscription ID)
S3_BUCKET_NAME = 'image-compressor-backup-nas'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:100458165777:image-compressor-alerts'

@app.route('/')
def index():
    return '''
        <h2>Image Compressor with S3 Backup & SNS Email Alert</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <input type="submit" value="Upload, Compress & Notify">
        </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    file_bytes = file.read()

    try:
        # 1. Backup the original image to S3
        s3_client.upload_fileobj(io.BytesIO(file_bytes), S3_BUCKET_NAME, file.filename)

        # 2. Process/Compress the image using Pillow
        image = Image.open(io.BytesIO(file_bytes))
        
        output_io = io.BytesIO()
        image.save(output_io, format='JPEG', quality=75)
        output_io.seek(0)

        # 3. Send an SNS email notification
        message = f"Success! The image '{file.filename}' was uploaded, backed up to S3 bucket '{S3_BUCKET_NAME}', and compressed."
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="Image Compression & S3 Backup Alert"
        )

        return f"<h3>{message}</h3><br><a href='/'>Upload Another</a>"

    except Exception as e:
        return f"Error processing image or communicating with AWS: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)