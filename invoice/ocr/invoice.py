import ast

from openai import chat
from logger import logger
from database.database import get_all_db_data, update_image_detail, update_revenue_expense
from ocr.helper import get_openai_client, encode_image
from invoice_config import INVOICE_PROMPT, OPENAI_MODEL, TABLE_NAME

def read_db_image_to_details(cursor, conn, openai_api_key):
    for id, image_blob, details in get_all_db_data(cursor, TABLE_NAME):

        if details is None:
            details = analyze_image(image_blob, openai_api_key)
            update_image_detail(cursor, conn, id, 'details', details)
            update_revenue_expense(cursor, conn, id, details, 'revenue_expense')

def analyze_image(image_blob, openai_api_key):
    client = get_openai_client(openai_api_key)
    base64_image = encode_image(image_blob)

    if base64_image is not None:
        chatgpt_messages = [{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": INVOICE_PROMPT,
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }]

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=chatgpt_messages)

        response_text = response.choices[0].message.content
        valid_dict1 = extract_valid_dict(response_text, chatgpt_messages, OPENAI_MODEL, client, additional_text='')
        response_vat_dict = extract_valid_vat_dict(repr(valid_dict1), chatgpt_messages, OPENAI_MODEL, client)
        valid_dict2 = extract_valid_dict(repr(response_vat_dict), chatgpt_messages, OPENAI_MODEL, client)
        return valid_dict2

def prepare_chatgpt_msg(text, chatgpt_messages):
    chatgpt_messages.append({"role": "user", "content": text})
    return chatgpt_messages

def chatgpt_request_extraction(msgs, model_name, client):
    response = client.chat.completions.create(model=model_name, messages=msgs)
    return response


def extract_valid_dict(response_text, chatgpt_messages, model_name, client, additional_text='', max_attempts=5):
    attempt = 0
    #chatgpt_messages = []

    while attempt < max_attempts:
        try:
            extracted_dict = ast.literal_eval(response_text)
            if isinstance(extracted_dict, dict):
                return extracted_dict
                
        except (SyntaxError, ValueError):
            logger.info(f"Attempt: {attempt + 1} to extract the Python dictionary from the text. The current dictionary is: {repr(response_text)}")
            attempt += 1
            cur_content = f"The previous {attempt + 1} attempt to extract of the valid Python dictionary from the text failed.\n" \
                            f"The previous result was: {response_text}\n" \
                            "Extract valid Python dictionary with no additional text, formatting, or code. The output should look exactly like this: {\"...\"}.\n" \
                            "Provide only the dictionary, nothing else.\n" + additional_text
            
            chatgpt_messages = prepare_chatgpt_msg(cur_content, chatgpt_messages)
            extraction_response = chatgpt_request_extraction(chatgpt_messages, model_name, client)
            response_text = extraction_response.choices[0].message.content
    
    raise ValueError("Failed to extract a valid Python list after multiple attempts.")

def valid_vat_total(response_json):
    indication = response_json["total_price"] == response_json["total_price_before_VAT"] + response_json["VAT_amount"]
    return indication

def valid_vat(response_json):
    percent = 1 - (response_json["total_price"] / response_json["total_price_before_VAT"])
    extracted_vat = response_json["VAT_rate"] if response_json["VAT_rate"] < 1 else response_json["VAT_rate"] / 100
    indication = (percent == extracted_vat) and (response_json("VAT_amount")/response_json("total_proce_before_VAT"))
    return indication
 
def valid_total_price(response_json):
    indication = response_json["total_price"] == response_json["total_price_before_VAT"] + response_json["VAT_amount"]

    return indication

def extract_valid_vat_dict(response_json, chatgpt_messages, model_name, client, additional_text='', max_attempts=5):
    attempt = 0
    chatgpt_messages = []

    while attempt < max_attempts:
        if valid_total_price and valid_vat:
           return response_json
        else:     
           logger.info(f"Attempt: {attempt + 1} to extract the valid VAT. The current dictionary is: {repr(response_json)}")
           attempt += 1
           cur_content = f"The previous {attempt + 1} attempt to extract of the valid prices from the image into dictionary failed.\n" \
                         f"The previous result was: {response_text}\n" \
                         "Make sure that: 'total_price' = 'total_price_before_VAT' + 'VAT_amount' and 'VAT_rate' = 'VAT_amount' / 'total_price_before_VAT'\n" \
                         "Extract valid Python dictionary with no additional text, formatting, or code. The output should look exactly like this: {\"...\"}.\n" \
                         "Provide only the dictionary, nothing else.\n" + additional_text
            
           chatgpt_messages = prepare_chatgpt_msg(cur_content, chatgpt_messages)
           extraction_response = chatgpt_request_extraction(chatgpt_messages, model_name, client)
           response_text = extraction_response.choices[0].message.content
    
    raise ValueError("Failed to extract a valid Python list after multiple attempts.")

#IMAGE_PATH = "2.jpeg"  # Change this to your image path
#result = analyze_image(IMAGE_PATH, OPENAI_API_KEY)
#print(result)
