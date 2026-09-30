import io
import re
import easyocr
import numpy as np
from PIL import Image, UnidentifiedImageError

class OCRService:
    def __init__(self):
        self._reader = None

    @property
    def reader(self):
        """Lazy initialization of EasyOCR reader to ensure fast server startup."""
        if self._reader is None:
            self._reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        return self._reader

    def extract_text(self, image_bytes: bytes) -> dict:
        try:
            # Safely open the image using Pillow
            image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if it has an alpha channel or is not in standard format
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Convert to numpy array for EasyOCR
            image_np = np.array(image)

            # Read text using lazy reader
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
        text = text.strip()
        text = re.sub(r'[^\S\r\n]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text
