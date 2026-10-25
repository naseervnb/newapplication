import io
import os
import zipfile
from flask import Flask, request, render_template, send_file
from PIL import Image
import boto3

app = Flask(__name__)

# Initialize AWS clients
s3_client = boto3.client('s3', region_name='us-east-1')
sns_client = boto3.client('sns', region_name='us-east-1')

# Configurations
S3_BUCKET_NAME = 'image-compressor-backup-nas'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:100458165777:image-compressor-alerts'

@app.route('/')
def index():
    return '''
        <h2>Advanced Image Compressor & Folder Backup</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <p><b>Option 1: Select Multiple Files (Any type: Images, PSD, XML, PPT, etc.)</b></p>
            <input type="file" name="files" multiple><br><br>
            
            <p><b>Option 2: Select an Entire Folder (Supports subfolders)</b></p>
            <input type="file" name="folder" webkitdirectory directory multiple><br><br>
            
            <input type="submit" value="Process, Backup & Download ZIP">
        </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_files():
    # Gather files from both single/multi file picker and folder picker
    uploaded_files = request.files.getlist('files') + request.files.getlist('folder')
    
    if not uploaded_files or uploaded_files[0].filename == '':
        return "No files or folder selected", 400

    # Create an in-memory zip file to return all processed files to the user
    memory_zip = io.BytesIO()

    try:
        with zipfile.ZipFile(memory_zip, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for file in uploaded_files:
                if not file.filename:
                    continue
                
                file_path = file.filename  # Preserves relative subfolder paths from folder upload
                file_bytes = file.read()
                file_ext = file_path.lower().split('.')[-1]

                print(f"Processing: {file_path}")

                # 1. Always back up original file to S3 maintaining its path/name
                s3_client.upload_fileobj(io.BytesIO(file_bytes), S3_BUCKET_NAME, file_path)

                # 2. Check if it's an image file we want to compress
                image_extensions = ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff']
                if file_ext in image_extensions:
                    try:
                        image = Image.open(io.BytesIO(file_bytes))
                        
                        # Convert RGBA/Palette images to RGB for JPEG compatibility
                        if image.mode in ('RGBA', 'P'):
                            image = image.convert('RGB')

                        output_io = io.BytesIO()
                        image.save(output_io, format='JPEG', quality=75)
                        output_io.seek(0)
                        
                        # Change extension to .jpg for compressed version in output
                        out_filename = file_path.rsplit('.', 1)[0] + '_compressed.jpg'
                        zip_out.writestr(out_filename, output_io.read())
                    except Exception as img_err:
                        print(f"Failed to compress image {file_path}, copying as-is. Error: {img_err}")
                        zip_out.writestr(file_path, file_bytes)
                else:
                    # 3. Copy other files (.psd, .xml, .xlsx, .ppt, etc.) as-is into the converted folder structure
                    zip_out.writestr(file_path, file_bytes)

        memory_zip.seek(0)

        # 4. Send SNS notification
        message = f"Success! Processed multiple files/folders, backed up originals to S3 bucket '{S3_BUCKET_NAME}', and generated downloadable package."
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="Batch Image Compression & S3 Backup Alert"
        )

        # 5. Return everything neatly packaged as a ZIP download
        return send_file(
            memory_zip,
            mimetype='application/zip',
            as_attachment=True,
            download_name='converted_and_backed_up_files.zip'
        )

    except Exception as e:
        print(f"ERROR OCCURRED: {str(e)}")
        return f"Error processing batch/folder: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)