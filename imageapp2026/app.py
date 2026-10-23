from flask import Flask, request
from PIL import Image
import boto3
import io

# 1. Initialize Flask FIRST
app = Flask(__name__)

# 2. THEN define your routes using @app.route
@app.route('/upload', methods=['POST'])
def upload_image():
    # Your upload, S3 backup, and compression logic here...
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)