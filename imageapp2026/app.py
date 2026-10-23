import os
import io
import boto3
from datetime import datetime
from flask import Flask, request, send_file
from PIL import Image

app = Flask(__name__)

# AWS Configuration
REGION_NAME = 'ap-south-1'  # Change to your AWS region if different
S3_BUCKET_NAME = 'your-s3-bucket-name'  # Replace with your actual S3 bucket name
MY_PHONE_NUMBER = '+918248882101'

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=REGION_NAME)
sns_client = boto3.client('sns', region_name=REGION_NAME)

def notify_user(message):
    try:
        sns_client.publish(
            PhoneNumber=MY_PHONE_NUMBER,
            Message=message
        )
    except Exception as e:
        print(f"SNS Notification Error: {e}")

def upload_original_to_s3(file_storage, filename):
    try:
        # Create a unique filename with a timestamp for the original file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        s3_key = f"original-images/{timestamp}_{filename}"
        
        # Reset file stream position to the beginning before reading
        file_storage.seek(0)
        
        s3_client.upload_fileobj(
            file_storage,
            S3_BUCKET_NAME,
            s3_key
        )
        return s3_key
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return None

HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
    <title>Image Compressor & Original Backup</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; background: #f4f4f9; text-align: center; }
        .card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: inline-block; }
        input[type=file] { margin: 20px 0; }
        input[type=submit] { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        input[type=submit]:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Image Compressor</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="image/*" required><br>
            <input type="submit" value="Compress and Download">
        </form>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return HTML_TEMPLATE
        
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            return 'No selected file'
            
        try:
            # 1. Upload a copy of the ORIGINAL file to S3
            s3_path = upload_original_to_s3(file, file.filename)
            
            # 2. Process and compress the image for user download
            file.seek(0)  # Reset stream again for Pillow
            img = Image.open(file.stream)
            output = io.BytesIO()
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.save(output, format='JPEG', quality=60)
            output.seek(0)
            
            # 3. Send SMS Notification via AWS SNS
            if s3_path:
                notify_user(f"Success! Original image '{file.filename}' was backed up to S3 and compressed version downloaded.")
            else:
                notify_user(f"Alert: Image '{file.filename}' processed, but S3 backup failed.")
            
            return send_file(
                output, 
                mimetype='image/jpeg', 
                as_attachment=True, 
                download_name='compressed_' + file.filename
            )
        except Exception as e:
            return f"Error processing image: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)