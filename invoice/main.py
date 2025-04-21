import os

from dotenv import load_dotenv
from backend.insert_imgs_db import process_images
from create_csv.db_to_csv import db2csv_main
from database.database import initialize_database
from invoice_config import DB_FILE, TABLE_NAME
from logger import logger
from ocr.invoice import read_db_image_to_details

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    logger.info("%s Start %s", "-" * 20, "-" * 20)
    conn, cursor = initialize_database(DB_FILE, TABLE_NAME)
    process_images(conn, cursor)
    read_db_image_to_details(cursor, conn, OPENAI_API_KEY)
    db2csv_main(conn)
    conn.close()
    logger.info("%s Finished %s", "-" * 20, "-" * 20)
