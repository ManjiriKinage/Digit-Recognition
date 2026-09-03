# 🖋️ Handwritten Digit Recognition System (MNIST + CNN + Flask)

An end-to-end deep learning web application that recognizes handwritten digits (0–9) drawn interactively on an HTML5 canvas or uploaded via image files. Powered by a Convolutional Neural Network (CNN) trained on the MNIST dataset, served by a Flask REST backend, with real-time probability distribution visualization.

---

## 🌟 Features

- **Interactive Canvas**: High-precision HTML5 drawing canvas with adjustable brush sizes, eraser, and instant clear.
- **Deep CNN Architecture**: Multi-layer Convolutional Neural Network with Batch Normalization and Dropout achieving **~99.2% test accuracy** on MNIST.
- **Robust Image Preprocessing**: OpenCV-based grayscale extraction, aspect-ratio preserving bounding-box cropping, padding, and center-of-mass alignment matching MNIST's exact representation.
- **Full Softmax Probability Breakdown**: Real-time animated progress bars displaying probability distributions across all 10 digits (0 through 9).
- **AI Neural Preview**: Displays the exact 28×28 normalized tensor as processed by the neural network.
- **Image Upload & Preset Digits**: Drag-and-drop digit image file uploads or test with pre-built vector samples.
- **Session History**: Track recent predictions with confidence scores and execution latencies.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │       USER          │
                    │ Draw / Upload Digit │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │   Frontend / UI     │
                    │ HTML + Tailwind CSS │
                    │ Canvas              │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │      Flask API      │
                    │ Receive Image       │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │  Image Processing   │
                    │ • Grayscale         │
                    │ • Bounding Box Crop │
                    │ • Center of Mass    │
                    │ • Resize 28×28      │
                    │ • Normalize 0–1     │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │   Trained CNN Model │
                    │   digit_model.keras │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │     Prediction      │
                    │ Digit: 7            │
                    │ Confidence: 98.5%   │
                    │ 0-9 Probabilities   │
                    └─────────────────────┘
```

---

## 📁 Project Structure

```text
Digit Recognition/
├── app.py                  # Flask REST API and inference endpoints
├── train.py                # Dataset download, CNN training, evaluation & metrics
├── digit_model.keras       # Serialized trained CNN model
├── requirements.txt        # Project dependencies
├── training_history.png    # Training & validation loss/accuracy curves
├── confusion_matrix.png    # Evaluation confusion matrix heatmap
├── templates/
│   └── index.html          # Frontend web layout
├── static/
│   ├── style.css           # Glassmorphic dark styling & animations
│   └── script.js           # Canvas drawing engine & API integration
└── README.md               # Documentation
```

---

## 🚀 Quick Start

### 1. Install Dependencies

Ensure Python 3.10+ is installed, then run:

```bash
pip install -r requirements.txt
```

### 2. Train the CNN Model

Train the model on the MNIST dataset (60,000 train images / 10,000 test images):

```bash
python train.py
```

This will:
- Train the CNN for 12 epochs with early stopping and learning rate scheduling.
- Output test accuracy and classification metrics.
- Save the model to `digit_model.keras`.
- Generate `training_history.png` and `confusion_matrix.png`.

### 3. Start the Web Server

Run the Flask application:

```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔌 API Endpoints

### `GET /`
Renders the interactive web application.

### `GET /health`
Returns model availability status.
```json
{
  "status": "online",
  "model_loaded": true,
  "model_path": "digit_model.keras"
}
```

### `POST /predict`
Performs digit classification.

**JSON Request:**
```json
{
  "image": "data:image/png;base64,iVBORw0KGgo..."
}
```

**JSON Response:**
```json
{
  "success": true,
  "digit": 7,
  "confidence": 98.65,
  "probabilities": [
    {"digit": 0, "percentage": 0.01, "is_predicted": false},
    {"digit": 1, "percentage": 0.05, "is_predicted": false},
    {"digit": 7, "percentage": 98.65, "is_predicted": true}
  ],
  "processed_image": "data:image/png;base64,..."
}
```
