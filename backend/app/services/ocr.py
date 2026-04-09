import re

import cv2
import numpy as np
import pytesseract


def extract_vin_from_image(image_bytes: bytes) -> str | None:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Preprocess
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    text = pytesseract.image_to_string(gray, config='--psm 6')
    # VIN pattern: 17 alphanumeric (no I,O,Q)
    pattern = r'[A-HJ-NPR-Z0-9]{17}'
    matches = re.findall(pattern, text.upper())
    if matches:
        return matches[0]
    return None