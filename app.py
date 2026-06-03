from __future__ import annotations

import random
from typing import Any

from flask import Flask, jsonify, render_template, request

from game_logic import decidir_vencedor, validar_numero
from opencv_utils import decode_base64_image, detect_fingers_opencv, encode_image_to_base64

app = Flask(__name__)


@app.get("/")
def index():
    """Página principal do jogo."""
    return render_template("index.html")


@app.post("/play")
def play():
    """Recebe a jogada do usuário, processa a imagem com OpenCV e retorna o resultado."""
    payload: dict[str, Any] = request.get_json(silent=True) or {}

    escolha = str(payload.get("choice", "")).strip().lower()
    numero_manual = payload.get("manualNumber")
    image_data = payload.get("image")

    if escolha not in {"par", "impar"}:
        return jsonify({"error": "Escolha inválida. Selecione 'par' ou 'ímpar'."}), 400

    detected_number = None
    confidence = 0.0
    debug_image_base64 = None
    opencv_message = "Nenhuma imagem recebida. Usando número manual."

    if image_data:
        try:
            frame = decode_base64_image(image_data)
            detected_number, confidence, debug_frame, opencv_message = detect_fingers_opencv(frame)
            debug_image_base64 = encode_image_to_base64(debug_frame)
        except Exception as exc:
            opencv_message = f"Não foi possível processar a imagem com OpenCV: {exc}"

    try:
        manual_number_int = validar_numero(numero_manual) if numero_manual not in (None, "") else None
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if detected_number is not None and confidence >= 0.45:
        user_number = detected_number
        source = "opencv"
    elif manual_number_int is not None:
        user_number = manual_number_int
        source = "manual"
    else:
        return jsonify({
            "error": "Não consegui identificar os dedos pela câmera. Informe também um número manual entre 0 e 5."
        }), 400

    computer_number = random.randint(0, 5)
    result = decidir_vencedor(escolha, user_number, computer_number)

    return jsonify({
        "choice": escolha,
        "userNumber": user_number,
        "computerNumber": computer_number,
        "total": result["total"],
        "parity": result["parity"],
        "winner": result["winner"],
        "source": source,
        "detectedNumber": detected_number,
        "confidence": round(confidence, 2),
        "opencvMessage": opencv_message,
        "debugImage": debug_image_base64,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
