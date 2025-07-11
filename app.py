import os
import json
import numpy as np
from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model
import cv2

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables for model and class names
model = None
class_names = []
disease_info = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_disease_info():
    """Load disease information and remedies"""
    global disease_info
    try:
        with open('data/disease_info.json', 'r') as f:
            disease_info = json.load(f)
    except FileNotFoundError:
        # Default disease info if file doesn't exist
        disease_info = {
            "Apple___Apple_scab": {
                "description": "Apple scab is a fungal disease that affects apple trees and their fruit.",
                "symptoms": "Dark, scaly lesions on leaves and fruit",
                "remedies": [
                    "Apply fungicides containing sulfur or copper",
                    "Remove infected leaves and fruit",
                    "Improve air circulation around trees",
                    "Plant resistant apple varieties"
                ]
            },
            "Apple___Black_rot": {
                "description": "Black rot is a fungal disease that causes dark lesions on apple leaves and fruit.",
                "symptoms": "Brown to black circular spots on leaves, rotting fruit",
                "remedies": [
                    "Remove infected plant parts",
                    "Apply fungicides in early spring",
                    "Ensure proper drainage",
                    "Prune to improve air circulation"
                ]
            },
            "Apple___Cedar_apple_rust": {
                "description": "Cedar apple rust is a fungal disease that alternates between cedar and apple trees.",
                "symptoms": "Yellow spots on leaves that develop orange spore masses",
                "remedies": [
                    "Remove nearby cedar trees if possible",
                    "Apply fungicides during wet periods",
                    "Plant resistant apple varieties",
                    "Remove infected leaves"
                ]
            },
            "Apple___healthy": {
                "description": "The plant appears to be healthy with no visible signs of disease.",
                "symptoms": "Green, vibrant leaves with no spots or discoloration",
                "remedies": [
                    "Continue regular watering and fertilization",
                    "Monitor for any changes in plant health",
                    "Maintain good garden hygiene",
                    "Ensure adequate sunlight and air circulation"
                ]
            },
            "Corn_(maize)___Cercospora_leaf_spot": {
                "description": "Cercospora leaf spot is a fungal disease affecting corn plants.",
                "symptoms": "Small, rectangular gray or tan spots with dark borders on leaves",
                "remedies": [
                    "Apply fungicides containing strobilurin",
                    "Practice crop rotation",
                    "Remove crop debris after harvest",
                    "Plant resistant corn varieties"
                ]
            },
            "Corn_(maize)___Common_rust": {
                "description": "Common rust is a fungal disease that creates rust-colored pustules on corn leaves.",
                "symptoms": "Small, reddish-brown pustules on leaves",
                "remedies": [
                    "Apply fungicides if infection is severe",
                    "Plant resistant corn hybrids",
                    "Ensure proper plant spacing",
                    "Remove infected plant debris"
                ]
            },
            "Corn_(maize)___Northern_Leaf_Blight": {
                "description": "Northern leaf blight is a fungal disease causing elongated lesions on corn leaves.",
                "symptoms": "Long, elliptical gray-green lesions on leaves",
                "remedies": [
                    "Apply fungicides containing azoxystrobin",
                    "Practice crop rotation with non-host crops",
                    "Plant resistant corn varieties",
                    "Manage crop residue properly"
                ]
            },
            "Corn_(maize)___healthy": {
                "description": "The corn plant appears healthy with no visible disease symptoms.",
                "symptoms": "Green, upright leaves with no lesions or discoloration",
                "remedies": [
                    "Continue proper fertilization program",
                    "Monitor for pest and disease pressure",
                    "Maintain adequate soil moisture",
                    "Ensure proper plant spacing"
                ]
            }
        }

def load_ml_model():
    """Load the trained CNN model"""
    global model, class_names
    try:
        model = load_model('models/plant_disease_model.h5')
        with open('models/class_names.json', 'r') as f:
            class_names = json.load(f)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Model will be trained first...")

def preprocess_image(image_path):
    """Preprocess image for model prediction"""
    try:
        # Load and resize image
        img = cv2.imread(image_path)
        img = cv2.resize(img, (224, 224))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype('float32') / 255.0
        img = np.expand_dims(img, axis=0)
        return img
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

def predict_disease(image_path):
    """Predict plant disease from image"""
    if model is None:
        return {"error": "Model not loaded. Please train the model first."}
    
    processed_img = preprocess_image(image_path)
    if processed_img is None:
        return {"error": "Error processing image"}
    
    try:
        # Make prediction
        predictions = model.predict(processed_img)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        
        if len(class_names) > predicted_class_idx:
            predicted_class = class_names[predicted_class_idx]
        else:
            predicted_class = f"Unknown_Class_{predicted_class_idx}"
        
        # Get disease information
        disease_data = disease_info.get(predicted_class, {
            "description": "Disease information not available.",
            "symptoms": "Symptoms not documented.",
            "remedies": ["Consult with local agricultural extension service"]
        })
        
        return {
            "disease": predicted_class,
            "confidence": confidence,
            "description": disease_data["description"],
            "symptoms": disease_data["symptoms"],
            "remedies": disease_data["remedies"]
        }
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid conflicts
        import time
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Predict disease
        result = predict_disease(file_path)
        result['image_path'] = f"static/uploads/{filename}"
        
        return jsonify(result)
    
    return jsonify({'error': 'Invalid file type'})

@app.route('/train_model')
def train_model_route():
    """Route to trigger model training"""
    from train_model import train_cnn_model
    try:
        train_cnn_model()
        load_ml_model()  # Reload the newly trained model
        return jsonify({'success': 'Model trained successfully!'})
    except Exception as e:
        return jsonify({'error': f'Training failed: {str(e)}'})

@app.route('/model_status')
def model_status():
    """Check if model is loaded"""
    return jsonify({
        'model_loaded': model is not None,
        'num_classes': len(class_names) if class_names else 0
    })

if __name__ == '__main__':
    # Load disease information
    load_disease_info()
    
    # Try to load model
    load_ml_model()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)