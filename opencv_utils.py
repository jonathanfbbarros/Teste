from __future__ import annotations

import base64
import math
from typing import Optional

import cv2
import numpy as np


def decode_base64_image(data_url: str) -> np.ndarray:
    """Converte imagem base64 do navegador para matriz OpenCV BGR."""
    if "," in data_url:
        data_url = data_url.split(",", 1)[1]
    image_bytes = base64.b64decode(data_url)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("imagem inválida")
    return image


def encode_image_to_base64(image: np.ndarray) -> str:
    """Converte imagem OpenCV BGR para data URL base64."""
    ok, buffer = cv2.imencode(".jpg", image)
    if not ok:
        return ""
    encoded = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def _angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Calcula o ângulo ABC, usado para contar vales entre dedos."""
    ab = a - b
    cb = c - b
    dot = float(np.dot(ab, cb))
    norm = float(np.linalg.norm(ab) * np.linalg.norm(cb))
    if norm == 0:
        return 180.0
    cosine = max(-1.0, min(1.0, dot / norm))
    return math.degrees(math.acos(cosine))


def detect_fingers_opencv(frame: np.ndarray) -> tuple[Optional[int], float, np.ndarray, str]:
    """
    Tenta detectar quantidade de dedos levantados usando OpenCV.

    Usa segmentação simples de pele + contornos + convexity defects.
    Funciona melhor com fundo limpo, boa iluminação e mão centralizada.
    """
    debug = frame.copy()
    height, width = debug.shape[:2]

    x1, y1 = int(width * 0.18), int(height * 0.12)
    x2, y2 = int(width * 0.82), int(height * 0.92)
    roi = frame[y1:y2, x1:x2]

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    lower1 = np.array([0, 30, 60], dtype=np.uint8)
    upper1 = np.array([25, 180, 255], dtype=np.uint8)
    lower2 = np.array([160, 30, 60], dtype=np.uint8)
    upper2 = np.array([180, 180, 255], dtype=np.uint8)

    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask = cv2.bitwise_or(mask1, mask2)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.GaussianBlur(mask, (7, 7), 0)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cv2.rectangle(debug, (x1, y1), (x2, y2), (255, 255, 255), 2)

    if not contours:
        cv2.putText(debug, "Mao nao detectada", (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        return None, 0.0, debug, "OpenCV não encontrou uma mão na imagem."

    contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(contour)
    roi_area = roi.shape[0] * roi.shape[1]

    if area < roi_area * 0.04:
        cv2.putText(debug, "Aproxime a mao", (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        return None, 0.15, debug, "A mão parece pequena ou distante da câmera."

    contour_global = contour + np.array([[x1, y1]])
    cv2.drawContours(debug, [contour_global], -1, (0, 255, 0), 2)

    hull = cv2.convexHull(contour, returnPoints=False)
    if hull is None or len(hull) < 3:
        return None, 0.2, debug, "Não foi possível calcular o contorno da mão."

    defects = cv2.convexityDefects(contour, hull)
    if defects is None:
        fingers = 0
        confidence = 0.50
    else:
        valid_defects = 0
        for i in range(defects.shape[0]):
            s, e, f, depth = defects[i, 0]
            start = contour[s][0]
            end = contour[e][0]
            far = contour[f][0]

            angle = _angle(start, far, end)
            depth_px = depth / 256.0

            if angle <= 90 and depth_px > 18:
                valid_defects += 1
                cv2.circle(debug, (far[0] + x1, far[1] + y1), 7, (0, 0, 255), -1)

        fingers = min(valid_defects + 1, 5) if valid_defects > 0 else 0
        confidence = min(0.95, 0.45 + (valid_defects * 0.12))

    _x, _y, w, h = cv2.boundingRect(contour)
    aspect_ratio = h / max(w, 1)
    if fingers == 0 and aspect_ratio > 1.45 and area > roi_area * 0.08:
        fingers = 1
        confidence = max(confidence, 0.48)

    cv2.putText(debug, f"Dedos detectados: {fingers}", (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(debug, f"Confianca: {confidence:.2f}", (30, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    return int(fingers), float(confidence), debug, "Imagem processada com OpenCV."
