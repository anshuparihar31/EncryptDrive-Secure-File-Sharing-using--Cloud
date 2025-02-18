from flask import Flask, render_template, request, jsonify, send_file
import os
import io
import boto3
from werkzeug.utils import secure_filename
from encryption_utils import encrypt_file, decrypt_file  # Import from your encryption utils

# Flask setup
app = Flask(__name__, template_folder='../frontend')  # Serve templates from the frontend folder
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded files (unused now)
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# AWS S3 setup
s3_client = boto3.client('s3')
BUCKET_NAME = 'secure-file-transfer-bucket'

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route to render the file upload form (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    password = request.form.get('password')

    if not file or not password:
        return jsonify({'message': 'Please select a file and enter a password'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        try:
            # Encrypt the file data
            encrypted_file = encrypt_file(file.read(), password)
            
            # Upload the encrypted file to S3
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=filename,
                Body=encrypted_file
            )

            return jsonify({'message': f'File successfully uploaded and encrypted to S3: {filename}'}), 200
        except Exception as e:
            return jsonify({'message': f'Error during file upload: {str(e)}'}), 500
    else:
        return jsonify({'message': 'File type not allowed'}), 400

# Route to list all uploaded files from S3
@app.route('/list-files', methods=['GET'])
def list_files():
    try:
        # List files in the S3 bucket
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        files = [obj['Key'] for obj in response.get('Contents', [])]
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'message': f'Error retrieving file list: {str(e)}'}), 500

# Route to handle file download and decryption from S3
@app.route('/download/<filename>', methods=['POST'])
def download_file(filename):
    password = request.json.get('password')
    if not password:
        return jsonify({'error': 'Password is required'}), 400

    try:
        # Retrieve the encrypted file from S3
        s3_object = s3_client.get_object(Bucket=BUCKET_NAME, Key=filename)
        encrypted_data = s3_object['Body'].read()

        # Decrypt the file data
        decrypted_data = decrypt_file(encrypted_data, password)

        # Return the decrypted file as an attachment
        return send_file(
            io.BytesIO(decrypted_data),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': f'Failed to decrypt or download file: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
