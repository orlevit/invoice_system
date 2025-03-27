import os
from logger import logger
from dotenv import load_dotenv
from database.database import initialize_database
from backend.insert_imgs_db import process_images
from invoice_config import DB_FILE, TABLE_NAME
from ocr.invoice import read_db_image_to_details
from create_csv.db_to_csv import create_csv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    logger.info("-" * 20 + " Start" + "-" * 20)
    conn, cursor = initialize_database(DB_FILE, TABLE_NAME)
    process_images(conn, cursor)
    read_db_image_to_details(cursor, conn, OPENAI_API_KEY)
    create_csv(conn)
    conn.close()
    logger.info("-" * 20 + " Finished " + "-" * 20)
