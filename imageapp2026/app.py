import io
import os
from flask import Flask, request, render_template
from PIL import Image
import boto3

app = Flask(__name__)

# Initialize AWS clients
s3_client = boto3.client('s3', region_name='us-east-1')
sns_client = boto3.client('sns', region_name='us-east-1')

# Configurations
S3_BUCKET_NAME = 'image-compressor-backup-nas'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:100458165777:image-compressor-alerts'
CONVERTED_DIR = 'converted'

@app.route('/')
def index():
    return '''
        <h2>Image Compressor & Folder Organizer</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <fieldset style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;">
                <legend><b>Option A: Select Individual Files (Any type: Images, PSD, XML, PPT, etc.)</b></legend>
                <input type="file" name="files" multiple>
            </fieldset>

            <fieldset style="border: 1px solid #ccc; padding: 10px; margin-bottom: 15px;">
                <legend><b>Option B: Select an Entire Folder (Supports subfolders)</b></legend>
                <input type="file" name="folder" webkitdirectory directory multiple>
            </fieldset>

            <input type="submit" value="Process, Back up & Convert" style="padding: 8px 15px; font-weight: bold;">
        </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_files():
    # Gather files from both the file picker and the folder picker
    uploaded_files = request.files.getlist('files') + request.files.getlist('folder')
    
    # Filter out empty entries
    uploaded_files = [f for f in uploaded_files if f.filename]

    if not uploaded_files:
        return "No files or folder selected", 400

    processed_count = 0

    try:
        for file in uploaded_files:
            file_path = file.filename  # Maintains relative subfolder paths if a folder was chosen
            file_bytes = file.read()
            file_ext = file_path.lower().split('.')[-1]

            print(f"Processing: {file_path}")

            # 1. Back up original file to S3 maintaining its exact path/name
            s3_client.upload_fileobj(io.BytesIO(file_bytes), S3_BUCKET_NAME, file_path)

            # 2. Determine local save path inside the 'converted' folder
            local_save_path = os.path.join(CONVERTED_DIR, file_path)
            os.makedirs(os.path.dirname(local_save_path), exist_ok=True)

            # 3. Check if it's an image file to compress
            image_extensions = ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff']
            if file_ext in image_extensions:
                try:
                    image = Image.open(io.BytesIO(file_bytes))
                    
                    # Convert RGBA/Palette images to RGB for JPEG compatibility
                    if image.mode in ('RGBA', 'P'):
                        image = image.convert('RGB')

                    # Save compressed image as JPG inside the converted folder structure
                    out_path = os.path.splitext(local_save_path)[0] + '_compressed.jpg'
                    image.save(out_path, format='JPEG', quality=75)
                except Exception as img_err:
                    print(f"Failed to compress image {file_path}, copying as-is. Error: {img_err}")
                    with open(local_save_path, 'wb') as f:
                        f.write(file_bytes)
            else:
                # 4. Copy non-image files (.psd, .xml, .xlsx, .ppt, etc.) as-is into the converted folder
                with open(local_save_path, 'wb') as f:
                    f.write(file_bytes)
            
            processed_count += 1

        # 5. Send SNS email notification
        message = f"Success! Processed {processed_count} files/folders, backed up originals to S3 bucket '{S3_BUCKET_NAME}', and generated local 'converted' folder."
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="Batch Processing & S3 Backup Alert"
        )

        return f'''
            <h3>Success!</h3>
            <p>Processed <b>{processed_count}</b> files/folders.</p>
            <p>Originals safely backed up to S3 bucket: <b>{S3_BUCKET_NAME}</b></p>
            <p>Processed files and subfolders structured inside the server's <b>'{CONVERTED_DIR}'</b> directory.</p>
            <br><a href="/">Process Another Batch</a>
        '''

    except Exception as e:
        print(f"ERROR OCCURRED: {str(e)}")
        return f"Error processing batch/folder: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)