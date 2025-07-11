// Global variables
let currentResult = null;

// DOM elements
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const statusText = document.getElementById('status-text');
const statusIndicator = document.getElementById('status-indicator');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    checkModelStatus();
    setupSmoothScrolling();
});

// Setup event listeners
function setupEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop events
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Click to upload
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Navigation smooth scrolling
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', handleNavClick);
    });
    
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }
}

// Check model status
async function checkModelStatus() {
    try {
        const response = await fetch('/model_status');
        const data = await response.json();
        
        if (data.model_loaded) {
            statusText.textContent = `Model loaded - ${data.num_classes} classes available`;
            statusIndicator.classList.add('ready');
        } else {
            statusText.textContent = 'Model not loaded - Click "Train Model" to initialize';
            statusIndicator.classList.remove('ready');
        }
    } catch (error) {
        console.error('Error checking model status:', error);
        statusText.textContent = 'Error checking model status';
        statusIndicator.classList.remove('ready');
    }
}

// Handle drag over
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

// Handle drag leave
function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

// Handle drop
function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// Handle file select
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

// Handle file processing
function handleFile(file) {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
        showError('Please select a valid image file (JPG, PNG, GIF)');
        return;
    }
    
    // Validate file size (16MB max)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('File size must be less than 16MB');
        return;
    }
    
    // Show loading state
    showLoading();
    
    // Create form data and upload
    const formData = new FormData();
    formData.append('file', file);
    
    uploadFile(formData);
}

// Upload file to server
async function uploadFile(formData) {
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
        } else {
            showResults(data);
        }
    } catch (error) {
        console.error('Upload error:', error);
        showError('Error uploading file. Please try again.');
    }
}

// Show loading state
function showLoading() {
    uploadArea.classList.add('hidden');
    results.classList.add('hidden');
    loading.classList.remove('hidden');
}

// Show results
function showResults(data) {
    currentResult = data;
    
    // Hide loading
    loading.classList.add('hidden');
    
    // Update result content
    document.getElementById('uploaded-image').src = data.image_path;
    document.getElementById('disease-name').textContent = formatDiseaseName(data.disease);
    document.getElementById('disease-description').textContent = data.description;
    document.getElementById('disease-symptoms').textContent = data.symptoms;
    
    // Update confidence badge
    const confidenceBadge = document.getElementById('confidence-badge');
    const confidence = Math.round(data.confidence * 100);
    confidenceBadge.textContent = `${confidence}% Confidence`;
    
    // Set confidence level class
    confidenceBadge.className = 'confidence-badge';
    if (confidence >= 80) {
        confidenceBadge.classList.add('high');
    } else if (confidence >= 60) {
        confidenceBadge.classList.add('medium');
    } else {
        confidenceBadge.classList.add('low');
    }
    
    // Update remedies list
    const remediesList = document.getElementById('disease-remedies');
    remediesList.innerHTML = '';
    data.remedies.forEach(remedy => {
        const li = document.createElement('li');
        li.textContent = remedy;
        remediesList.appendChild(li);
    });
    
    // Show results
    results.classList.remove('hidden');
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Show error message
function showError(message) {
    loading.classList.add('hidden');
    uploadArea.classList.remove('hidden');
    results.classList.add('hidden');
    
    // Create error notification
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-notification';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add error styles if not already added
    if (!document.querySelector('.error-notification-styles')) {
        const styles = document.createElement('style');
        styles.className = 'error-notification-styles';
        styles.textContent = `
            .error-notification {
                position: fixed;
                top: 100px;
                right: 20px;
                background: linear-gradient(135deg, #ef4444, #dc2626);
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
                display: flex;
                align-items: center;
                gap: 0.75rem;
                z-index: 9999;
                animation: slideIn 0.3s ease;
                max-width: 400px;
            }
            
            .error-notification button {
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                padding: 0.25rem;
                border-radius: 4px;
                transition: background 0.3s ease;
            }
            
            .error-notification button:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(errorDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 5000);
}

// Reset upload area
function resetUpload() {
    uploadArea.classList.remove('hidden');
    results.classList.add('hidden');
    loading.classList.add('hidden');
    fileInput.value = '';
    currentResult = null;
    
    // Scroll to upload area
    uploadArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Format disease name for display
function formatDiseaseName(diseaseName) {
    return diseaseName
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase())
        .replace(/([a-z])([A-Z])/g, '$1 $2');
}

// Train model
async function trainModel() {
    const btn = event.target;
    const originalText = btn.innerHTML;
    
    // Show loading state
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Training...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/train_model');
        const data = await response.json();
        
        if (data.success) {
            showSuccess('Model trained successfully!');
            checkModelStatus(); // Refresh model status
        } else {
            showError(data.error || 'Training failed');
        }
    } catch (error) {
        console.error('Training error:', error);
        showError('Error starting model training');
    } finally {
        // Restore button
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Show success message
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-notification';
    successDiv.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add success styles if not already added
    if (!document.querySelector('.success-notification-styles')) {
        const styles = document.createElement('style');
        styles.className = 'success-notification-styles';
        styles.textContent = `
            .success-notification {
                position: fixed;
                top: 100px;
                right: 20px;
                background: linear-gradient(135deg, #22c55e, #16a34a);
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
                display: flex;
                align-items: center;
                gap: 0.75rem;
                z-index: 9999;
                animation: slideIn 0.3s ease;
                max-width: 400px;
            }
            
            .success-notification button {
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                padding: 0.25rem;
                border-radius: 4px;
                transition: background 0.3s ease;
            }
            
            .success-notification button:hover {
                background: rgba(255, 255, 255, 0.2);
            }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(successDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (successDiv.parentElement) {
            successDiv.remove();
        }
    }, 5000);
}

// Download report
function downloadReport() {
    if (!currentResult) {
        showError('No diagnosis results to download');
        return;
    }
    
    const reportContent = generateReportContent(currentResult);
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `plant-diagnosis-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    showSuccess('Report downloaded successfully!');
}

// Generate report content
function generateReportContent(result) {
    const date = new Date().toLocaleDateString();
    const confidence = Math.round(result.confidence * 100);
    
    return `
PLANT DISEASE DIAGNOSIS REPORT
Generated by PlantDoc AI
Date: ${date}

DIAGNOSIS RESULTS
================
Disease: ${formatDiseaseName(result.disease)}
Confidence: ${confidence}%

DESCRIPTION
===========
${result.description}

SYMPTOMS
========
${result.symptoms}

RECOMMENDED TREATMENT
====================
${result.remedies.map((remedy, index) => `${index + 1}. ${remedy}`).join('\n')}

DISCLAIMER
==========
This diagnosis is provided by an AI system and should be used as a guide only. 
For critical decisions, please consult with a qualified agricultural expert or extension service.

Report generated by PlantDoc AI - Plant Disease Detection System
Powered by CNN Technology and PlantVillage Dataset
`.trim();
}

// Scroll to upload section
function scrollToUpload() {
    document.getElementById('upload').scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
    });
}

// Handle navigation clicks
function handleNavClick(e) {
    e.preventDefault();
    const targetId = e.target.getAttribute('href').substring(1);
    const targetElement = document.getElementById(targetId);
    
    if (targetElement) {
        targetElement.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
        
        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        e.target.classList.add('active');
    }
}

// Setup smooth scrolling for navigation
function setupSmoothScrolling() {
    // Update active nav link on scroll
    window.addEventListener('scroll', () => {
        const sections = ['home', 'upload', 'about'];
        const navLinks = document.querySelectorAll('.nav-link');
        
        let current = '';
        
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                const rect = section.getBoundingClientRect();
                if (rect.top <= 100 && rect.bottom >= 100) {
                    current = sectionId;
                }
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

// Header scroll effect
window.addEventListener('scroll', () => {
    const header = document.querySelector('.header');
    if (window.scrollY > 100) {
        header.style.background = 'rgba(255, 255, 255, 0.98)';
        header.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
    } else {
        header.style.background = 'rgba(255, 255, 255, 0.95)';
        header.style.boxShadow = 'none';
    }
});

// Image preview on hover (optional enhancement)
function previewImage(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.createElement('div');
        preview.className = 'image-preview';
        preview.innerHTML = `
            <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px; border-radius: 8px;">
        `;
        
        // You could add this preview to the upload area if desired
    };
    reader.readAsDataURL(file);
}

// Utility function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Add loading overlay for better UX during model training
function showTrainingOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'training-overlay';
    overlay.innerHTML = `
        <div class="training-content">
            <div class="training-spinner"></div>
            <h3>Training AI Model</h3>
            <p>This may take several minutes...</p>
            <div class="training-progress">
                <div class="progress-bar"></div>
            </div>
        </div>
    `;
    
    // Add overlay styles
    const styles = document.createElement('style');
    styles.textContent = `
        #training-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }
        
        .training-content {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            text-align: center;
            max-width: 400px;
        }
        
        .training-spinner {
            width: 60px;
            height: 60px;
            border: 4px solid #f3f4f6;
            border-top: 4px solid #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1.5rem;
        }
        
        .training-progress {
            width: 100%;
            height: 6px;
            background: #f3f4f6;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 1rem;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            width: 0%;
            animation: progress 30s linear infinite;
        }
        
        @keyframes progress {
            from { width: 0%; }
            to { width: 100%; }
        }
    `;
    
    document.head.appendChild(styles);
    document.body.appendChild(overlay);
    
    return overlay;
}

// Remove training overlay
function hideTrainingOverlay() {
    const overlay = document.getElementById('training-overlay');
    if (overlay) {
        overlay.remove();
    }
}