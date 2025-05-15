# file: lambda_app.py
import json, base64, cv2, numpy as np, requests, logging
from src import segment_image

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def _load_image(image_data: str):
    """Recebe URL ou data-URI base64 e devolve numpy image BGR ou None."""
    if image_data.startswith("http"):
        log.info("Baixando imagem…")
        r = requests.get(image_data, timeout=30)
        r.raise_for_status()
        return cv2.imdecode(np.frombuffer(r.content, np.uint8), cv2.IMREAD_COLOR)

    log.info("Decodificando base64…")
    try:
        img_bytes = base64.b64decode(image_data.split(",")[-1])
        return cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    except Exception:
        return None

def lambda_handler(event, context):
    """Único ponto de entrada HTTP (API Gateway / Lambda URL)."""

    # Quando o API Gateway HTTP API envia a requisição como JSON:
    body = event.get("body")
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode()

    try:
        payload = json.loads(body)
    except Exception:
        return {"statusCode": 400,
                "body": json.dumps({"error": "Body must be JSON"})}

    img_field = payload.get("image")
    if not img_field:
        return {"statusCode": 400,
                "body": json.dumps({"error": "No image field"})}

    image = _load_image(img_field)
    if image is None:
        return {"statusCode": 400,
                "body": json.dumps({"error": "Invalid or unreadable image"})}

    contour = segment_image(image)
    if contour is None:
        return {"statusCode": 404,
                "body": json.dumps({"error": "No contour found"})}

    contour_list = contour.reshape(-1, 2).tolist()
    return {"statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"contour": contour_list})}
