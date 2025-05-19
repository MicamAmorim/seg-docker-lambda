import streamlit as st
import requests
import numpy as np
import cv2
import os
import tempfile
import base64
import json

API_URL = "http://localhost:9000/2015-03-31/functions/function/invocations"

st.title("Segmentação de Imagens com API")

uploaded_file = st.file_uploader("Envie uma imagem ou tire uma foto", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Salva a imagem temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(uploaded_file.read())
        image_path = temp_file.name
    
    # Lê a imagem para exibir
    image = cv2.imread(image_path)
    st.image(image, channels="BGR", caption="Imagem Original", use_container_width=True)
    
    # Converte a imagem para base64 para envio na API
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()
        image_base64 = base64.b64encode(image_bytes).decode()
        
    # Faz a requisição para a API
    payload = {"body": f"{{\"image\": \"data:image/jpeg;base64,{image_base64}\"}}"}
    try:
        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        
        # Extrai o contorno do campo "body" (JSON aninhado)
        response_body = json.loads(response.json()["body"])
        contour = np.array(response_body["contour"], dtype=np.int32)
        
        # Cria a máscara
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)
        
        # Aplica a máscara verde na imagem original
        overlay = image.copy()
        overlay[mask > 0] = (0, 255, 0)  # máscara verde
        blended = cv2.addWeighted(overlay, 0.5, image, 0.5, 0)
        
        # Exibe a imagem segmentada
        st.image(blended, channels="BGR", caption="Imagem Segmentada", use_container_width=True)
        st.success("Segmentação aplicada com sucesso!")
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na requisição para a API: {e}")
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
    
    # Remove o arquivo temporário
    os.remove(image_path)

