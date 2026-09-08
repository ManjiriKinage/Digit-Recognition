---
title: Handwritten Digit Recognition
emoji: 🖋️
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

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

---

## 🌐 Deployment Guide

### Option 1: Deploy on Render (Recommended & Free)
1. Push this project repository to GitHub.
2. Sign up / Log in to [Render](https://render.com).
3. Click **New +** → **Web Service** and connect your GitHub repository.
4. Render will automatically detect the settings from [render.yaml](file:///d:/projects2/Digit%20Recognition/render.yaml) or you can manually configure:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120`
5. Click **Create Web Service**.

---

### Option 2: Deploy on Railway
1. Push your repository to GitHub.
2. Go to [Railway](https://railway.app) and click **New Project** → **Deploy from GitHub repo**.
3. Railway automatically detects the [Dockerfile](file:///d:/projects2/Digit%20Recognition/Dockerfile) / [Procfile](file:///d:/projects2/Digit%20Recognition/Procfile) and deploys your service.

---

### Option 3: Deploy on Hugging Face Spaces (Free ML Hosting)
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Select **Docker** as the SDK (Blank template) and choose **Public** or **Private**.
3. Clone the Space repo or upload your project files (`app.py`, `templates/`, `static/`, `digit_model.keras`, `requirements.txt`, `Dockerfile`).
4. Hugging Face will automatically build the container and serve the app at `https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`.

---

### Option 4: Deploy using Docker (Any VPS / Cloud)

#### Build Docker Image:
```bash
docker build -t digit-recognition:latest .
```

#### Run Container:
```bash
docker run -d -p 5000:5000 --name digit-app digit-recognition:latest
```

Access the app at `http://localhost:5000`.

