# 🌱 PlantDoc AI - Plant Disease Detection System

An AI-powered web application for plant disease detection using Convolutional Neural Networks (CNN) and the PlantVillage dataset. Upload a photo of your plant leaf and get instant disease diagnosis with recommended treatments.

![PlantDoc AI](https://img.shields.io/badge/AI-Plant%20Disease%20Detection-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13.0-orange)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red)

## 🚀 Features

- **AI-Powered Diagnosis**: Advanced CNN model trained on PlantVillage dataset
- **Multi-Plant Support**: Detects diseases in Apple, Corn, Tomato, and more
- **Real-time Results**: Instant disease classification with confidence scores
- **Treatment Recommendations**: Detailed remedies and prevention strategies
- **Beautiful UI**: Modern, responsive design that works on all devices
- **Drag & Drop Upload**: Easy image upload with drag-and-drop functionality
- **Report Generation**: Download detailed diagnosis reports
- **Model Training**: Built-in model training capabilities

## 🏗️ Architecture

### Frontend
- **HTML5** with modern semantic structure
- **CSS3** with advanced gradients, animations, and responsive design
- **JavaScript (ES6+)** for interactive functionality
- **Font Awesome** icons and **Google Fonts**

### Backend
- **Flask** web framework
- **TensorFlow/Keras** for deep learning
- **OpenCV** for image processing
- **PIL (Pillow)** for image manipulation

### Machine Learning
- **CNN Architecture**: Custom 5-layer convolutional neural network
- **Data Augmentation**: Rotation, scaling, and flipping for robust training
- **Transfer Learning Ready**: Easily adaptable for new plant species
- **Model Persistence**: Save and load trained models

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- At least 4GB RAM (8GB recommended for training)
- Modern web browser

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/plantdoc-ai.git
cd plantdoc-ai
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Open your browser**
Navigate to `http://localhost:5000`

## 🎯 Usage

### 1. Train the Model (First Time Setup)
- Click the "Train Model" button on the homepage
- Wait for the training process to complete (this may take several minutes)
- The model will be saved automatically for future use

### 2. Diagnose Plant Diseases
- Navigate to the "Diagnose" section
- Upload an image by:
  - Clicking "Choose Image" and selecting a file
  - Dragging and dropping an image onto the upload area
- Wait for the AI analysis
- Review the results including:
  - Disease classification
  - Confidence score
  - Detailed description
  - Symptoms to look for
  - Treatment recommendations

### 3. Download Reports
- After diagnosis, click "Download Report" to get a detailed text file
- Share results with agricultural experts or keep for records

## 🧪 Supported Plant Diseases

### Apple
- Apple Scab
- Black Rot
- Cedar Apple Rust
- Healthy

### Corn (Maize)
- Cercospora Leaf Spot
- Common Rust
- Northern Leaf Blight
- Healthy

### Tomato
- Bacterial Spot
- Early Blight
- Late Blight
- Healthy

*More plant species and diseases coming soon!*

## 📊 Model Architecture

```
Layer (type)                 Output Shape              Param #   
=================================================================
conv2d (Conv2D)              (None, 222, 222, 32)     896       
batch_normalization          (None, 222, 222, 32)     128       
max_pooling2d (MaxPooling2D) (None, 111, 111, 32)     0         
conv2d_1 (Conv2D)            (None, 109, 109, 64)     18496     
batch_normalization_1        (None, 109, 109, 64)     256       
max_pooling2d_1              (None, 54, 54, 64)       0         
conv2d_2 (Conv2D)            (None, 52, 52, 128)      73856     
batch_normalization_2        (None, 52, 52, 128)      512       
max_pooling2d_2              (None, 26, 26, 128)      0         
conv2d_3 (Conv2D)            (None, 24, 24, 256)      295168    
batch_normalization_3        (None, 24, 24, 256)      1024      
max_pooling2d_3              (None, 12, 12, 256)      0         
conv2d_4 (Conv2D)            (None, 10, 10, 512)      1180160   
batch_normalization_4        (None, 10, 10, 512)      2048      
max_pooling2d_4              (None, 5, 5, 512)        0         
flatten (Flatten)            (None, 12800)             0         
dense (Dense)                (None, 1024)              13107200  
dropout (Dropout)            (None, 1024)              0         
dense_1 (Dense)              (None, 512)               524800    
dropout_1 (Dropout)          (None, 512)               0         
dense_2 (Dense)              (None, num_classes)       varies    
=================================================================
```

## 🔧 Configuration

### Model Training Parameters
- **Image Size**: 224x224 pixels
- **Batch Size**: 32
- **Epochs**: 50 (with early stopping)
- **Learning Rate**: 0.001 (with reduction on plateau)
- **Data Augmentation**: Enabled

### File Upload Settings
- **Max File Size**: 16MB
- **Supported Formats**: JPG, JPEG, PNG, GIF
- **Processing**: Automatic resize to 224x224

## 📁 Project Structure

```
plantdoc-ai/
├── app.py                 # Main Flask application
├── train_model.py         # CNN model training script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── data/
│   ├── disease_info.json # Disease information database
│   └── PlantVillage/     # Dataset (created during training)
├── models/
│   ├── plant_disease_model.h5  # Trained model
│   └── class_names.json        # Class labels
├── static/
│   ├── css/
│   │   └── style.css     # Styles
│   ├── js/
│   │   └── script.js     # JavaScript functionality
│   ├── images/           # Static images
│   └── uploads/          # Uploaded images
└── templates/
    └── index.html        # Main HTML template
```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment

#### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🧪 Testing

### Upload Test Images
1. Find sample plant disease images online
2. Test with different image formats and sizes
3. Verify confidence scores and recommendations

### Model Performance
- Training accuracy: ~95%+
- Validation accuracy: ~90%+
- Test accuracy: ~88%+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📈 Future Enhancements

- [ ] Add more plant species (Potato, Pepper, Grape, etc.)
- [ ] Implement user authentication and history
- [ ] Add mobile app version
- [ ] Integrate with agricultural databases
- [ ] Real-time camera capture
- [ ] GPS location tracking for field use
- [ ] Multi-language support
- [ ] API for third-party integration

## 🐛 Troubleshooting

### Common Issues

**Model not loading**
- Ensure the model file exists in `models/plant_disease_model.h5`
- Check that TensorFlow is properly installed
- Try training the model first

**Upload errors**
- Verify file size is under 16MB
- Check file format is supported (JPG, PNG, GIF)
- Ensure upload directory has write permissions

**Training fails**
- Check available memory (need at least 4GB RAM)
- Verify TensorFlow installation
- Check disk space for dataset download

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PlantVillage Dataset** - Training data source
- **TensorFlow Team** - Deep learning framework
- **Flask Community** - Web framework
- **Agricultural Research Community** - Domain expertise

## 📞 Support

- **Email**: support@plantdoc-ai.com
- **Issues**: [GitHub Issues](https://github.com/yourusername/plantdoc-ai/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/plantdoc-ai/wiki)

## 🌟 Show Your Support

Give a ⭐️ if this project helped you!

---

**Built with ❤️ for sustainable agriculture and AI-powered farming solutions.**