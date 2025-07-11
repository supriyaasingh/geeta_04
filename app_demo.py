import os
import json
import numpy as np
import random
import time
from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
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
model_loaded = True  # Simulate model is always loaded in demo
class_names = [
    "Apple___Apple_scab",
    "Apple___Black_rot", 
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Corn_(maize)___Cercospora_leaf_spot",
    "Corn_(maize)___Common_rust",
    "Corn_(maize)___Northern_Leaf_Blight", 
    "Corn_(maize)___healthy"
]
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

def analyze_image_color(image_path):
    """Analyze image colors to make an educated guess about plant health"""
    try:
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        
        # Define color ranges for different conditions
        # Green (healthy)
        lower_green = np.array([40, 30, 30])
        upper_green = np.array([80, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        green_ratio = np.sum(green_mask > 0) / (img.shape[0] * img.shape[1])
        
        # Brown/Yellow (diseased)
        lower_brown = np.array([10, 50, 50])
        upper_brown = np.array([30, 255, 255])
        brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
        brown_ratio = np.sum(brown_mask > 0) / (img.shape[0] * img.shape[1])
        
        return green_ratio, brown_ratio
    except:
        return 0.5, 0.3  # Default values

def simulate_cnn_prediction(image_path):
    """Simulate CNN model prediction based on image analysis"""
    # Analyze image colors
    green_ratio, brown_ratio = analyze_image_color(image_path)
    
    # Extract filename to make educated guesses
    filename = os.path.basename(image_path).lower()
    
    # Base probabilities for different conditions
    if green_ratio > 0.3 and brown_ratio < 0.2:
        # Likely healthy
        if 'apple' in filename:
            predicted_class = "Apple___healthy"
            confidence = 0.85 + random.uniform(0, 0.1)
        elif 'corn' in filename or 'maize' in filename:
            predicted_class = "Corn_(maize)___healthy"
            confidence = 0.87 + random.uniform(0, 0.08)
        else:
            # Random healthy class
            healthy_classes = [c for c in class_names if 'healthy' in c]
            predicted_class = random.choice(healthy_classes)
            confidence = 0.82 + random.uniform(0, 0.12)
    else:
        # Likely diseased
        if 'apple' in filename:
            disease_classes = [c for c in class_names if 'Apple' in c and 'healthy' not in c]
            predicted_class = random.choice(disease_classes)
            confidence = 0.78 + random.uniform(0, 0.15)
        elif 'corn' in filename or 'maize' in filename:
            disease_classes = [c for c in class_names if 'Corn' in c and 'healthy' not in c]
            predicted_class = random.choice(disease_classes)
            confidence = 0.75 + random.uniform(0, 0.18)
        else:
            # Random disease class based on color analysis
            if brown_ratio > 0.3:
                # More likely to be a spot/blight disease
                spot_diseases = [c for c in class_names if any(word in c.lower() for word in ['spot', 'blight', 'scab'])]
                predicted_class = random.choice(spot_diseases) if spot_diseases else random.choice(class_names)
            else:
                predicted_class = random.choice(class_names)
            confidence = 0.72 + random.uniform(0, 0.2)
    
    return predicted_class, min(confidence, 0.98)  # Cap confidence at 98%

def predict_disease(image_path):
    """Predict plant disease from image using simulated CNN"""
    try:
        # Simulate processing time
        time.sleep(random.uniform(1, 3))
        
        # Simulate CNN prediction
        predicted_class, confidence = simulate_cnn_prediction(image_path)
        
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
    """Simulate model training"""
    try:
        # Simulate training time
        time.sleep(random.uniform(2, 5))
        return jsonify({'success': 'Demo model is ready! (This is a simulation for demonstration purposes)'})
    except Exception as e:
        return jsonify({'error': f'Training simulation failed: {str(e)}'})

@app.route('/model_status')
def model_status():
    """Check if model is loaded (always true in demo)"""
    return jsonify({
        'model_loaded': True,
        'num_classes': len(class_names),
        'demo_mode': True,
        'message': 'Running in demo mode with simulated AI predictions'
    })

if __name__ == '__main__':
    # Load disease information
    load_disease_info()
    
    print("=" * 60)
    print("🌱 PlantDoc AI - Demo Mode")
    print("=" * 60)
    print("This is a demonstration version that simulates AI predictions.")
    print("The system analyzes image colors and filenames to provide")
    print("realistic plant disease detection results.")
    print("=" * 60)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)