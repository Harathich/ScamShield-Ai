import io
import re
import easyocr
import numpy as np
from PIL import Image, UnidentifiedImageError

class OCRService:
    def __init__(self):
        # Initialize EasyOCR reader for English (and Hindi since it's common in Indian scams)
        # We use gpu=False by default for broader compatibility, but it could be configurable
        self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)

    def extract_text(self, image_bytes: bytes) -> dict:
        try:
            # Safely open the image using Pillow
            image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if it has an alpha channel or is not in standard format
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Convert to numpy array for EasyOCR
            image_np = np.array(image)

            # Read text
            results = self.reader.readtext(image_np)

            if not results:
                return {
                    "success": True,
                    "extracted_text": "",
                    "confidence": 0.0,
                    "language": None
                }

            texts = []
            confidences = []
            for (bbox, text, prob) in results:
                texts.append(text)
                confidences.append(prob)

            combined_text = "\n".join(texts)
            avg_confidence = float(sum(confidences) / len(confidences))

            # Normalize text
            normalized_text = self._normalize_text(combined_text)

            return {
                "success": True,
                "extracted_text": normalized_text,
                "confidence": avg_confidence,
                "language": None
            }

        except (UnidentifiedImageError, OSError, SyntaxError) as e:
            return {
                "success": False,
                "error": "The uploaded file is corrupt or not a valid image."
            }
        except ValueError as e:
            if "image" in str(e).lower() or "array" in str(e).lower():
                return {
                    "success": False,
                    "error": "Invalid image data."
                }
            raise e # Let genuine programming errors bubble up

    def _normalize_text(self, text: str) -> str:
        # Trim leading/trailing whitespace
        text = text.strip()

        # Replace multiple spaces with a single space (while keeping line breaks)
        # Using a regex that matches horizontal whitespace only
        text = re.sub(r'[^\S\r\n]+', ' ', text)

        # Replace 3 or more consecutive newlines with exactly 2
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text
