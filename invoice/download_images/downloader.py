import io
import os

import numpy as np
import pyheif
from database.database import image_exists, insert_image_to_db
from googleapiclient.http import MediaIoBaseDownload
from logger import logger
from PIL import Image
from sentence_transformers import SentenceTransformer


def setup_embedding_model():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info("Embedding model loaded.")
    return model

embedding_model = setup_embedding_model()

def compute_embedding(image):
    image = image.convert("RGB")  # Ensure it's in RGB format
    image = image.resize((224, 224))
    img_array = np.array(image).flatten()
    return embedding_model.encode(str(img_array)).tobytes()

def convert_to_jpg(file_name, fh):
    if file_name.lower().endswith(".heic"):
        heif_file = pyheif.read(fh)
        image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode, heif_file.stride)
    else:
        image = Image.open(fh).convert("RGB")

    return image
    

def download_and_save_image(service, cursor, conn, file_id, file_name, save_folder):
    
    if image_exists(cursor, file_id):
        logger.info(f"Image {file_name} already exists in the database. Skipping.")
        return
    
    request = service.files().get_media(fileId=file_id)
    file_path = os.path.join(save_folder, file_name)
    
    with io.BytesIO() as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.seek(0)

        converted_img = convert_to_jpg(file_name, fh)
        
    embedding = compute_embedding(converted_img)
    insert_image_to_db(cursor, conn, file_id, file_name, embedding, converted_img)
