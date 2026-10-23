from flask import Flask, render_template, request
from PIL import Image
import boto3
import io

app = Flask(__name__)

# 1. Home route to display your upload form/interface
@app.route('/')
def index():
    # If you have an HTML template, use: return render_template('index.html')
    # Or return a simple HTML string for testing:
    return '''
        <h2>Image Compressor with S3 Backup & SNS</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload & Compress">
        </form>
    '''

# 2. Upload route to handle the file, S3 backup, compression, and SNS alert
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # Read file bytes once for reuse
    file_bytes = file.read()

    # Backup original file to S3
    s3 = boto3.client('s3')
    s3.upload_fileobj(io.BytesIO(file_bytes), 'YOUR_S3_BUCKET_NAME', file.filename)

    # Process image with Pillow
    image = Image.open(io.BytesIO(file_bytes))
    # ... add your compression / SNS notification logic here ...

    return "Image processed successfully, backed up to S3, and notification sent!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)