import os
import io
from flask import Flask, request, send_file, render_template_string
from PIL import Image

app = Flask(__name__)

# Simple HTML template for the web upload interface
HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
    <title>Image Compressor Web App</title>
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
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            try:
                # Open image using Pillow
                img = Image.open(file.stream)
                
                # Compress and save to an in-memory buffer
                output = io.BytesIO()
                # Convert RGBA/Palette modes to RGB for safe JPEG saving
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                img.save(output, format='JPEG', quality=60)
                output.seek(0)
                
                return send_file(
                    output, 
                    mimetype='image/jpeg', 
                    as_attachment=True, 
                    download_name='compressed_' + file.filename
                )
            except Exception as e:
                return f"Error processing image: {str(e)}"
                
    return HTML_TEMPLATE

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)