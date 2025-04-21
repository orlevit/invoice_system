import os
import ast
import shutil
import pandas as pd
from logger import logger
from database.database import blob_to_image
from invoice_config import (
    EXPENSES_FILE,
    REVENUES_FILE,
    FAILED_IMAGES_FILE,
    TABLE_NAME,
    UNPREOCESSES_IMGS_DIR,
    OUTPUT_DIR,
)


def create_failed_images(conn):
    query = f"SELECT  name, image FROM {TABLE_NAME} WHERE revenue_expense IS NULL"
    cursor = conn.cursor()
    cursor.execute(query)
    
    count = 0
    for  name, img_blob in cursor.fetchall():
        if '.' in name:
            name = name.rsplit('.',1)[0]

        filename = f"{name}.jpg"
        path = os.path.join(UNPREOCESSES_IMGS_DIR, filename)

        img = blob_to_image(img_blob)
        img.save(path, format="JPEG")
        # with open(path, "wb") as f:
        #     f.write(img)
        count += 1

    logger.info("Could not extracts details of %d images. The images exist in %s", count, UNPREOCESSES_IMGS_DIR)


def clean_target_folder():
    if os.path.isdir(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.makedirs(UNPREOCESSES_IMGS_DIR, exist_ok=True)


def extract_json_details(df):
    details_data = df["details"].apply(lambda x: ast.literal_eval(x) if x else {})
    details_df = pd.json_normalize(details_data)
    return pd.concat([df.drop(columns=["details"]), details_df], axis=1)


def dump_to_csv(conn, revenue_expense, output_file):
    if revenue_expense is None:
        where_clause = "revenue_expense IS NULL"
    else:
        where_clause = f"revenue_expense = {revenue_expense}"

    query = f"SELECT name, details FROM {TABLE_NAME} WHERE {where_clause}"

    df = pd.read_sql(query, conn)
    df = extract_json_details(df)
    df.to_csv(output_file, index=False)


def create_csv(conn):
    dump_to_csv(conn, revenue_expense=0, output_file=EXPENSES_FILE)
    dump_to_csv(conn, revenue_expense=1, output_file=REVENUES_FILE)
    dump_to_csv(conn, revenue_expense=None, output_file=FAILED_IMAGES_FILE)


def db2csv_main(conn):
    clean_target_folder()
    create_csv(conn)
    create_failed_images(conn)
