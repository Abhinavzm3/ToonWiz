import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from flask import send_from_directory

app = Flask(__name__)

# Configure upload folder and allowed extensions
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['CARTOON_FOLDER'] = 'static/cartoonized'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CARTOON_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def cartoonize_image(img_path):
    # Read the image
    img = cv2.imread(img_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply median blur to reduce noise
    gray = cv2.medianBlur(gray, 5)
    
    # Detect edges using adaptive threshold
    edges = cv2.adaptiveThreshold(gray, 255, 
        cv2.ADAPTIVE_THRESH_MEAN_C, 
        cv2.THRESH_BINARY, 9, 9)
    
    # Apply bilateral filter to preserve edges while smoothing
    color = cv2.bilateralFilter(img, 9, 300, 300)
    
    # Combine the edge mask with the color image
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    
    return cartoon

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Check if file was uploaded
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    # If no file selected
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Save original file
        filename = secure_filename(file.filename)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(original_path)
        
        # Cartoonize the image
        cartoon_image = cartoonize_image(original_path)
        
        # Save cartoonized image
        cartoon_filename = f'cartoon_{filename}'
        cartoon_path = os.path.join(app.config['CARTOON_FOLDER'], cartoon_filename)
        cv2.imwrite(cartoon_path, cartoon_image)
        
        return render_template('result.html', 
                             original=filename, 
                             cartoon=cartoon_filename)
    
    return redirect(request.url)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['CARTOON_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)