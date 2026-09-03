import os
import re
import io
import base64
import numpy as np
import cv2
from PIL import Image
from flask import Flask, render_template, request, jsonify
import tensorflow as tf

app = Flask(__name__)

# Global model holder
MODEL = None
MODEL_PATH = "digit_model.keras"

def get_model():
    """Lazy load or cache trained Keras model."""
    global MODEL
    if MODEL is None:
        if os.path.exists(MODEL_PATH):
            print(f"Loading trained model from {MODEL_PATH}...")
            MODEL = tf.keras.models.load_model(MODEL_PATH)
        else:
            print(f"Warning: {MODEL_PATH} not found. Please run train.py first.")
    return MODEL

def center_image(img):
    """
    Center image using Center of Mass (similar to MNIST dataset standard processing).
    """
    cy, cx = cv2.moments(img)['m01'] / (cv2.moments(img)['m00'] + 1e-5), \
             cv2.moments(img)['m10'] / (cv2.moments(img)['m00'] + 1e-5)
    
    # Calculate shift needed to move center of mass to (14, 14)
    shift_x = np.round(14.0 - cx)
    shift_y = np.round(14.0 - cy)
    
    # Translation matrix
    M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    centered = cv2.warpAffine(img, M, (28, 28), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return centered

def preprocess_digit_image(image_bytes):
    """
    Process raw image bytes into a 28x28 normalized MNIST-like tensor:
    1. Decode image into grayscale.
    2. Ensure stroke is white (255) and background is black (0).
    3. Find bounding box of digit.
    4. Fit bounding box into 20x20 box preserving aspect ratio.
    5. Pad to 28x28 and center by center of mass.
    6. Normalize to [0.0, 1.0].
    """
    # Open with PIL to handle PNG transparency and various formats
    pil_image = Image.open(io.BytesIO(image_bytes))
    
    # If image has alpha channel, paste over white or black background
    if pil_image.mode in ('RGBA', 'LA') or (pil_image.mode == 'P' and 'transparency' in pil_image.info):
        alpha = pil_image.convert('RGBA').split()[-1]
        bg = Image.new("RGB", pil_image.size, (0, 0, 0)) # black background
        bg.paste(pil_image, mask=alpha)
        img_np = np.array(bg)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    else:
        gray = np.array(pil_image.convert('L'))
    
    # Determine if background is light or dark
    # In canvas or photo uploads, background is often white (255) and ink is black (0)
    # In MNIST, digit is white (255) on black (0)
    if np.mean(gray) > 127:
        gray = cv2.bitwise_not(gray)
    
    # Denoise / threshold slightly to remove faint background artifacts
    _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_TOZERO)
    
    # Find bounding box of the digit
    non_zero_pts = cv2.findNonZero(thresh)
    if non_zero_pts is None:
        return None, "Canvas is empty. Please draw a digit first."
    
    x, y, w, h = cv2.boundingRect(non_zero_pts)
    
    # Add a slight margin around the bounding box
    margin = 2
    x_start = max(0, x - margin)
    y_start = max(0, y - margin)
    x_end = min(gray.shape[1], x + w + margin)
    y_end = min(gray.shape[0], y + h + margin)
    
    cropped = thresh[y_start:y_end, x_start:x_end]
    
    # Scale into 20x20 box preserving aspect ratio
    ch, cw = cropped.shape
    if ch > cw:
        factor = 20.0 / ch
        new_h = 20
        new_w = max(1, int(round(cw * factor)))
    else:
        factor = 20.0 / cw
        new_w = 20
        new_h = max(1, int(round(ch * factor)))
    
    resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Pad resized digit to 28x28
    padded = np.zeros((28, 28), dtype=np.uint8)
    pad_top = (28 - new_h) // 2
    pad_left = (28 - new_w) // 2
    padded[pad_top:pad_top + new_h, pad_left:pad_left + new_w] = resized
    
    # Align by center of mass for MNIST compatibility
    try:
        final_28x28 = center_image(padded)
    except Exception:
        final_28x28 = padded
    
    # Generate base64 visualization of the processed 28x28 image for UI preview
    _, buffer = cv2.imencode('.png', final_28x28)
    processed_b64 = f"data:image/png;base64,{base64.b64encode(buffer).decode('utf-8')}"
    
    # Normalize tensor for CNN: [1, 28, 28, 1], float32 in [0.0, 1.0]
    tensor = final_28x28.astype("float32") / 255.0
    tensor = np.expand_dims(tensor, axis=(0, -1))
    
    return tensor, processed_b64

@app.route("/")
def index():
    """Serve the main web UI."""
    return render_template("index.html")

@app.route("/health", methods=["GET"])
def health():
    """Health check and model status."""
    model = get_model()
    return jsonify({
        "status": "online",
        "model_loaded": model is not None,
        "model_path": MODEL_PATH
    })

@app.route("/predict", methods=["POST"])
def predict():
    """Predict digit from base64 canvas image or file upload."""
    model = get_model()
    if model is None:
        return jsonify({
            "success": False,
            "error": "Model is not loaded. Please train the model with train.py first."
        }), 503
    
    image_bytes = None
    
    # Check if request has base64 json or multipart file
    if request.is_json:
        data = request.get_json()
        image_data = data.get("image", "")
        if not image_data:
            return jsonify({"success": False, "error": "No image data provided"}), 400
        
        # Remove data URI header if present
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({"success": False, "error": f"Invalid base64 string: {str(e)}"}), 400
            
    elif "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No selected file"}), 400
        image_bytes = file.read()
    else:
        return jsonify({"success": False, "error": "No image payload found in request"}), 400

    try:
        tensor, processed_preview = preprocess_digit_image(image_bytes)
        if tensor is None:
            return jsonify({"success": False, "error": processed_preview}), 400
        
        # Inference
        predictions = model.predict(tensor, verbose=0)[0]
        predicted_digit = int(np.argmax(predictions))
        confidence = float(predictions[predicted_digit] * 100)
        
        # Probabilities for all 10 classes
        probabilities = [
            {
                "digit": i,
                "percentage": round(float(prob * 100), 2),
                "is_predicted": (i == predicted_digit)
            }
            for i, prob in enumerate(predictions)
        ]
        
        return jsonify({
            "success": True,
            "digit": predicted_digit,
            "confidence": round(confidence, 2),
            "probabilities": probabilities,
            "processed_image": processed_preview
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Inference error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Handwritten Digit Recognition Web App on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
