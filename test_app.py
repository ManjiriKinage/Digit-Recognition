import unittest
import json
import io
import numpy as np
import cv2
from PIL import Image
import base64
from app import app, get_model, preprocess_digit_image

class DigitRecognitionTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_model_loading(self):
        """Test model is loaded and valid."""
        model = get_model()
        self.assertIsNotNone(model, "Model should be loaded from digit_model.keras")

    def test_health_endpoint(self):
        """Test GET /health."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "online")
        self.assertTrue(data.get("model_loaded"))

    def test_index_endpoint(self):
        """Test GET /."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Handwritten Digit AI", response.data)

    def test_predict_empty_canvas(self):
        """Test predicting an empty (all black) canvas returns 400."""
        # Create 280x280 black image
        blank_img = np.zeros((280, 280), dtype=np.uint8)
        _, buffer = cv2.imencode('.png', blank_img)
        b64 = "data:image/png;base64," + base64.b64encode(buffer).decode('utf-8')
        
        response = self.app.post('/predict',
                                json={'image': b64},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data.get('success'))

    def test_predict_drawn_digit_base64(self):
        """Test predicting a drawn digit '7' via Base64 JSON payload."""
        # Create 280x280 black canvas with white digit '7' drawn on it
        img = np.zeros((280, 280), dtype=np.uint8)
        # Draw digit 7
        cv2.putText(img, "7", (60, 220), cv2.FONT_HERSHEY_SIMPLEX, 7.0, (255,), 20, cv2.LINE_AA)
        
        _, buffer = cv2.imencode('.png', img)
        b64 = "data:image/png;base64," + base64.b64encode(buffer).decode('utf-8')

        response = self.app.post('/predict',
                                json={'image': b64},
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('digit', data)
        self.assertEqual(data.get('digit'), 7)
        self.assertIn('confidence', data)
        self.assertIn('probabilities', data)
        self.assertEqual(len(data.get('probabilities')), 10)
        self.assertIn('processed_image', data)

    def test_predict_file_upload(self):
        """Test predicting a digit via multipart file upload."""
        # Create digit '3' image (white background with black text)
        img = np.ones((200, 200), dtype=np.uint8) * 255
        cv2.putText(img, "3", (40, 160), cv2.FONT_HERSHEY_SIMPLEX, 5.0, (0,), 15, cv2.LINE_AA)
        
        _, buffer = cv2.imencode('.png', img)
        file_bytes = io.BytesIO(buffer.tobytes())

        response = self.app.post('/predict',
                                data={'file': (file_bytes, 'digit3.png')},
                                content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('digit'), 3)

    def test_invalid_request(self):
        """Test POST /predict without image payload."""
        response = self.app.post('/predict', data={})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
