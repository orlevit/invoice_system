import io
import pickle
import sqlite3
from PIL import Image
from logger import logger
from invoice_config import IMAGES_TABLE

def get_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

def is_table_exists(cursor, table_name):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None

def image_to_blob(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')  
    return img_byte_arr.getvalue()

def blob_to_image(blob):
    return Image.open(io.BytesIO(blob))

def embeddings_to_blob(embedding):
    return pickle.dumps(embedding) 

def blob_to_embeddings(blob):
    return pickle.loads(blob) 

def get_all_db_data(cursor, table_name):
    if not table_name.isidentifier():
        raise ValueError(f"Invalid table name: {table_name}")
    
    rows = cursor.execute(f"SELECT id, name, image, details FROM {table_name}").fetchall()

    for row in rows:
        yield row

def initialize_database(db_file, table_name):
    conn = get_connection(db_file)
    cursor = conn.cursor()
    
    if not is_table_exists(cursor, table_name):
        cursor.execute(IMAGES_TABLE.format(table_name))
        conn.commit()
        logger.info("Database initialized: 'images' table created.")
    else:
        logger.info("Database already initialized: 'images' table exists.")

    return conn, cursor

def image_exists(cursor, file_id):
    cursor.execute("SELECT id FROM images WHERE id = ?", (file_id,))
    return cursor.fetchone() is not None

def insert_image_to_db(cursor, conn, file_id, file_name, embedding, img):
    image_blob = image_to_blob(img)
    embedding_blob = embeddings_to_blob(embedding)
    cursor.execute("INSERT INTO images (id, name, embedding, image) VALUES (?, ?, ?, ?)",
                   (file_id, file_name, embedding_blob, image_blob))
    conn.commit()
    logger.info(f"Image added to database: {file_name}")

def update_image_detail(cursor, conn, file_id, column_name, new_value):
    query = f"UPDATE images SET {column_name} = ? WHERE id = ?"
    cursor.execute(query, (repr(new_value), file_id))
    conn.commit()
    logger.info(f"Updated {column_name} for image ID '{file_id}' with value: {new_value}")

def convert_revenue_expense(details):
    revenue_expense_text = details['revenue_expense']
    revenue_expense_num = None

    if revenue_expense_text == 'revenue':
        revenue_expense_num = 1
    elif revenue_expense_text == 'expense':
        revenue_expense_num = 0
    else:
        logger.error("revenue_expense field is incorrect format: {e}")
    
    return revenue_expense_num

def update_revenue_expense(cursor, conn, id, details, column_name):
    converted_revenue_expense = convert_revenue_expense(details)
    query = f"UPDATE images SET {column_name} = ? WHERE id = ?"
    cursor.execute(query, (converted_revenue_expense, id))
    conn.commit()
    logger.info(f"Updated {column_name} for image ID {id} with value: {converted_revenue_expense}")

