import onnxruntime as ort
import numpy as np
import cv2
from typing import Optional

# Configurações do modelo
MODEL_PATH = "models/best.onnx"
CONFIDENCE = 0.3
INPUT_WIDTH = 640
INPUT_HEIGHT = 640

# Carrega o modelo ONNX
providers = ['CPUExecutionProvider']
session_options = ort.SessionOptions()
session_options.log_severity_level = 4  # Apenas erros críticos
session = ort.InferenceSession(MODEL_PATH, providers=providers, sess_options=session_options)

# Obtem nomes das entradas e saídas do modelo
inname = [i.name for i in session.get_inputs()]
outname = [o.name for o in session.get_outputs()]

def _masks_to_contours(mask: np.ndarray) -> Optional[np.ndarray]:
    """Converte uma máscara binária para contorno."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        return max(contours, key=cv2.contourArea)  # Retorna o maior contorno
    return None


def segment_image(image: np.ndarray, confidence: float = CONFIDENCE) -> Optional[np.ndarray]:
    """Segmenta uma imagem usando ONNX e retorna o maior contorno ou None."""
    if image is None or image.size == 0:
        raise ValueError("Empty image provided to segment_image().")

    # Redimensiona a imagem para o tamanho de entrada do modelo
    original_height, original_width = image.shape[:2]
    resized_image = cv2.resize(image, (INPUT_WIDTH, INPUT_HEIGHT))
    rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)

    # Prepara o tensor de entrada
    input_tensor = rgb_image.astype(np.float32) / 255.0
    input_tensor = np.transpose(input_tensor, (2, 0, 1))  # HWC → CHW
    input_tensor = np.expand_dims(input_tensor, axis=0)   # (C, H, W) → (1, C, H, W)
    input_tensor = np.ascontiguousarray(input_tensor)     # Garante contiguidade

    # Executa a inferência
    outputs = session.run(outname, {inname[0]: input_tensor})

    # Extrai caixas e coeficientes de máscara
    boxes_and_coeffs = outputs[0][0]  # (300, 38)
    proto_masks = outputs[1][0]       # (32, H', W')

    # Filtra as detecções pela confiança mínima
    boxes = boxes_and_coeffs[:, :6]       # (300, 6)
    mask_coeffs = boxes_and_coeffs[:, 6:] # (300, 32)
    valid_indices = boxes[:, 4] > confidence
    boxes = boxes[valid_indices]
    mask_coeffs = mask_coeffs[valid_indices]

    # Decodifica as máscaras para o tamanho original
    if len(mask_coeffs) == 0:
        return None  # Nenhuma detecção válida

    largest_contour = None
    max_area = 0
    for coeff in mask_coeffs:
        # Cria a máscara a partir dos coeficientes
        mask = np.dot(proto_masks.transpose(1, 2, 0).reshape(-1, 32), coeff).reshape(proto_masks.shape[1:])
        mask = (mask > 0.5).astype(np.uint8) * 255  # Binariza para contorno

        # Redimensiona para o tamanho original
        mask_resized = cv2.resize(mask, (original_width, original_height))

        # Encontra o contorno e seleciona o maior
        contour = _masks_to_contours(mask_resized)
        if contour is not None:
            area = cv2.contourArea(contour)
            if area > max_area:
                max_area = area
                largest_contour = contour

    return largest_contour
