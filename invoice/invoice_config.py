import os

# Directories
CURRENT_DIRECTORY = os.getcwd()

# Google dirve 
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'credentials.json'
SAVE_FOLDER = "downloaded_images"
FOLDER_ID = "1GROiW6oVNdIrDme-psc5d7N1HWdnttqe"

# Database
DB_FILE = "images.db"
TABLE_NAME = "images"
IMAGES_TABLE ="""
        CREATE TABLE IF NOT EXISTS {} (
            id TEXT PRIMARY KEY,
            name TEXT,
            embedding BLOB,
            image BLOB,
            revenue_expense TINYINT, 
            details TEXT
        )
    """

# OpenAI
LOGGER_FILE = 'app.log'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"
INVOICE_PROMPT = """Extract the information from the invoice image written in the Hebrew language as a JSON file.\n\
Each invoice ia either "expense" or "revenue".Usually the revenue has the following details in the header: לויטס אברבך שרית, טהון 22 חולון, 0505489797.\
The JSON should be in the following format:
{
    "business_name": "...",
    "address": "...",
    "date": "...",
    "total_price": ...,
    "total_price_before_VAT": ...,
    "VAT_rate": ...,
    "VAT_amount": ...,
    "revenue_expense": (revenue/expense),
}\n
If values is unknown then insert the value: "unknown".\n
Only output the JSON without any text before or after the JSON.\n
Make sure that the JSON can be evaluated with Python eval() function.
As a reminder, the invoice is written in the Hebrew language."""
