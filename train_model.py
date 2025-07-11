import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import requests
import zipfile
import shutil

def download_sample_data():
    """Download and create a sample dataset structure for demo purposes"""
    print("Setting up sample dataset structure...")
    
    # Create dataset directories
    dataset_path = "data/PlantVillage"
    classes = [
        "Apple___Apple_scab",
        "Apple___Black_rot", 
        "Apple___Cedar_apple_rust",
        "Apple___healthy",
        "Corn_(maize)___Cercospora_leaf_spot",
        "Corn_(maize)___Common_rust",
        "Corn_(maize)___Northern_Leaf_Blight", 
        "Corn_(maize)___healthy"
    ]
    
    for split in ["train", "test"]:
        for class_name in classes:
            os.makedirs(f"{dataset_path}/{split}/{class_name}", exist_ok=True)
    
    # Generate synthetic data for demo (in real scenario, you'd download actual PlantVillage dataset)
    print("Generating sample training data...")
    
    for split in ["train", "test"]:
        num_samples = 100 if split == "train" else 20
        for class_name in classes:
            for i in range(num_samples):
                # Create synthetic RGB images (224x224x3)
                if "healthy" in class_name:
                    # Healthy plants - more green
                    img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
                    img[:, :, 1] = np.clip(img[:, :, 1] + 50, 0, 255)  # Add green
                else:
                    # Diseased plants - add brown/yellow spots
                    img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
                    # Add some disease-like patterns
                    spot_x, spot_y = np.random.randint(50, 174, 2)
                    img[spot_x:spot_x+50, spot_y:spot_y+50, 0] = np.clip(img[spot_x:spot_x+50, spot_y:spot_y+50, 0] + 80, 0, 255)
                    img[spot_x:spot_x+50, spot_y:spot_y+50, 1] = np.clip(img[spot_x:spot_x+50, spot_y:spot_y+50, 1] + 40, 0, 255)
                
                # Save as image
                from PIL import Image
                img_pil = Image.fromarray(img)
                img_pil.save(f"{dataset_path}/{split}/{class_name}/sample_{i}.jpg")
    
    print(f"Sample dataset created at {dataset_path}")
    return dataset_path, classes

def download_real_plantvillage_dataset():
    """
    Download the real PlantVillage dataset from Kaggle
    Note: This requires Kaggle API credentials
    """
    try:
        import kaggle
        print("Downloading PlantVillage dataset from Kaggle...")
        
        # Download PlantVillage dataset
        kaggle.api.dataset_download_files('emmarex/plantdisease', path='data/', unzip=True)
        
        # Organize the dataset
        dataset_path = "data/PlantVillage"
        if os.path.exists("data/PlantVillage"):
            print("PlantVillage dataset downloaded successfully!")
            
            # Get class names
            classes = sorted(os.listdir(f"{dataset_path}/train"))
            return dataset_path, classes
        else:
            print("Failed to download real dataset, using sample data...")
            return download_sample_data()
            
    except Exception as e:
        print(f"Error downloading real dataset: {e}")
        print("Using sample data instead...")
        return download_sample_data()

def create_cnn_model(num_classes, input_shape=(224, 224, 3)):
    """Create a CNN model for plant disease classification"""
    
    model = Sequential([
        # First Convolutional Block
        Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        BatchNormalization(),
        MaxPooling2D(2, 2),
        
        # Second Convolutional Block
        Conv2D(64, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D(2, 2),
        
        # Third Convolutional Block
        Conv2D(128, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D(2, 2),
        
        # Fourth Convolutional Block
        Conv2D(256, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D(2, 2),
        
        # Fifth Convolutional Block
        Conv2D(512, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D(2, 2),
        
        # Flatten and Dense layers
        Flatten(),
        Dense(1024, activation='relu'),
        Dropout(0.5),
        Dense(512, activation='relu'),
        Dropout(0.3),
        Dense(num_classes, activation='softmax')
    ])
    
    return model

def train_cnn_model():
    """Main function to train the CNN model"""
    print("Starting CNN model training for plant disease detection...")
    
    # Try to download real dataset, fallback to sample data
    try:
        dataset_path, classes = download_real_plantvillage_dataset()
    except:
        dataset_path, classes = download_sample_data()
    
    num_classes = len(classes)
    print(f"Number of classes: {num_classes}")
    print(f"Classes: {classes}")
    
    # Save class names
    os.makedirs('models', exist_ok=True)
    with open('models/class_names.json', 'w') as f:
        json.dump(classes, f, indent=2)
    
    # Data preprocessing and augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        fill_mode='nearest',
        validation_split=0.2
    )
    
    test_datagen = ImageDataGenerator(rescale=1./255)
    
    # Load training data
    train_generator = train_datagen.flow_from_directory(
        f'{dataset_path}/train',
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='training'
    )
    
    validation_generator = train_datagen.flow_from_directory(
        f'{dataset_path}/train',
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='validation'
    )
    
    # Load test data if available
    test_generator = None
    if os.path.exists(f'{dataset_path}/test'):
        test_generator = test_datagen.flow_from_directory(
            f'{dataset_path}/test',
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical'
        )
    
    # Create and compile model
    print("Creating CNN model...")
    model = create_cnn_model(num_classes)
    
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("Model architecture:")
    model.summary()
    
    # Callbacks
    callbacks = [
        ModelCheckpoint(
            'models/plant_disease_model.h5',
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=5,
            min_lr=0.0001
        )
    ]
    
    # Train the model
    print("Starting training...")
    epochs = 50
    
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // train_generator.batch_size,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // validation_generator.batch_size,
        epochs=epochs,
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate model
    if test_generator:
        print("Evaluating model on test data...")
        test_loss, test_accuracy = model.evaluate(test_generator)
        print(f"Test Accuracy: {test_accuracy:.4f}")
        
        # Generate predictions for classification report
        predictions = model.predict(test_generator)
        predicted_classes = np.argmax(predictions, axis=1)
        true_classes = test_generator.classes
        
        # Print classification report
        print("\nClassification Report:")
        print(classification_report(true_classes, predicted_classes, target_names=classes))
    
    # Plot training history
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('static/images/training_history.png')
    plt.close()
    
    print("Model training completed!")
    print(f"Model saved as: models/plant_disease_model.h5")
    print(f"Class names saved as: models/class_names.json")
    
    return model, classes

if __name__ == "__main__":
    train_cnn_model()