import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

from database.database import initialize_database
from download_images.downloader import download_and_save_image
from invoice_config import DB_FILE, FOLDER_ID, SAVE_FOLDER, SCOPES, SERVICE_ACCOUNT_FILE
from logger import logger

def authenticate_drive():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    logger.info("Authenticated with Google Drive API.")
    return build('drive', 'v3', credentials=creds)

def process_images(conn, cursor):
    service = authenticate_drive()
    #conn, cursor = initialize_database(DB_FILE)
    query = f"'{FOLDER_ID}' in parents and (mimeType contains 'image/')"
    page_token = None
    
    while True:
        results = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType)", pageToken=page_token).execute()
        images = results.get('files', [])
        if not images:
            logger.info("No new images found.")
            break
        
        for image in images:
            download_and_save_image(service, cursor, conn, image["id"], image["name"], SAVE_FOLDER)
        
        page_token = results.get('nextPageToken', None)
        if not page_token:
            break
    
    logger.info("Downloaded from Drive and save to DB completed.")