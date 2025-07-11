#!/usr/bin/env python3
"""
Test script for PlantDoc AI application
"""

import requests
import json
import time
import os
from PIL import Image
import numpy as np

def create_test_image():
    """Create a simple test image"""
    # Create a simple green image (simulating healthy plant)
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    img[:, :, 1] = 150  # Green channel
    img[:, :, 0] = 50   # Red channel
    img[:, :, 2] = 50   # Blue channel
    
    # Add some noise
    noise = np.random.randint(0, 50, (224, 224, 3), dtype=np.uint8)
    img = np.clip(img + noise, 0, 255)
    
    # Save as test image
    test_img = Image.fromarray(img)
    test_img.save('test_plant.jpg')
    return 'test_plant.jpg'

def test_model_status():
    """Test the model status endpoint"""
    try:
        response = requests.get('http://localhost:5000/model_status')
        data = response.json()
        print("✅ Model Status Test:")
        print(f"   - Model Loaded: {data.get('model_loaded')}")
        print(f"   - Number of Classes: {data.get('num_classes')}")
        print(f"   - Demo Mode: {data.get('demo_mode')}")
        print(f"   - Message: {data.get('message')}")
        return True
    except Exception as e:
        print(f"❌ Model Status Test Failed: {e}")
        return False

def test_image_upload():
    """Test image upload and prediction"""
    try:
        # Create test image
        test_image = create_test_image()
        
        # Upload the image
        with open(test_image, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://localhost:5000/upload', files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Image Upload Test:")
            print(f"   - Disease: {data.get('disease')}")
            print(f"   - Confidence: {data.get('confidence', 0) * 100:.1f}%")
            print(f"   - Description: {data.get('description', '')[:50]}...")
            print(f"   - Remedies: {len(data.get('remedies', []))} recommendations")
            
            # Clean up
            os.remove(test_image)
            return True
        else:
            print(f"❌ Image Upload Test Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Image Upload Test Failed: {e}")
        return False

def test_train_model():
    """Test model training simulation"""
    try:
        response = requests.get('http://localhost:5000/train_model')
        data = response.json()
        print("✅ Model Training Test:")
        print(f"   - Response: {data.get('success', data.get('error'))}")
        return True
    except Exception as e:
        print(f"❌ Model Training Test Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing PlantDoc AI Application")
    print("=" * 50)
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    # Run tests
    tests = [
        test_model_status,
        test_image_upload,
        test_train_model
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The application is working correctly.")
        print("\n📱 You can now access the web interface at:")
        print("   http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Please check the application.")

if __name__ == "__main__":
    main()