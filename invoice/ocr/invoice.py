import ast

from logger import logger
from database.database import get_all_db_data, update_image_detail, update_revenue_expense
from ocr.helper import get_openai_client, encode_image
from invoice_config import INVOICE_PROMPT, OPENAI_MODEL, TABLE_NAME

def read_db_image_to_details(cursor, conn, openai_api_key):
    for image_id, image_name, image_blob, details in get_all_db_data(cursor, TABLE_NAME):

        if details is None:
            logger.info("Extract details for image: %s", image_name)
            details = analyze_image(image_blob, openai_api_key)
            
            if details is not None:
                update_image_detail(cursor, conn, image_id, 'details', details)
                update_revenue_expense(cursor, conn, image_id, details, 'revenue_expense')

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

        if valid_dict1 is None:
            return None

        response_vat_dict = extract_valid_vat_dict(valid_dict1, chatgpt_messages, OPENAI_MODEL, client)
        return response_vat_dict

def prepare_chatgpt_msg(text, chatgpt_messages):
    chatgpt_messages.append({"role": "user", "content": text})
    return chatgpt_messages

def chatgpt_request_extraction(msgs, model_name, client):
    response = client.chat.completions.create(model=model_name, messages=msgs)
    return response

def round_and_compare(reference_number, number_to_round):
    decimal_part = str(reference_number).split('.')[-1]
    
    decimal_places = len(decimal_part) if '.' in str(reference_number) else 0
    
    rounded_number = round(number_to_round, decimal_places)

    if reference_number == rounded_number:
        return True 
    
    return False

def extract_valid_dict(response_text, chatgpt_messages, model_name, client, additional_text='', max_attempts=5):
    attempt = 0
    if isinstance(response_text, dict):
        return response_text

    while attempt < max_attempts:
        try:
            extracted_dict = ast.literal_eval(response_text)
            if isinstance(extracted_dict, dict):
                return extracted_dict
                
        except (SyntaxError, ValueError):
            logger.info(f"Attempt: {attempt + 1} to extract the Python dictionary from the text. The current dictionary is: {response_text}")
            attempt += 1
            cur_content = f"The previous {attempt + 1} attempt to extract of the valid Python dictionary from the text failed.\n" \
                            f"The previous result was: {repr(response_text)}\n" \
                            "Extract valid Python dictionary with no additional text, formatting, or code. The output should look exactly like this: {\"...\"}.\n" \
                            "Provide only the dictionary, nothing else.\n" + additional_text
            
            chatgpt_messages = prepare_chatgpt_msg(cur_content, chatgpt_messages)
            extraction_response = chatgpt_request_extraction(chatgpt_messages, model_name, client)
            response_text = extraction_response.choices[0].message.content

    return None 
    # raise ValueError("Failed to extract a valid Python dictionary after multiple attempts.")

def check_type(response_json):
    # Check if all values are numbers and then check the equality
    if (isinstance(response_json["total_price"], (int, float)) and
        isinstance(response_json["total_price_before_VAT"], (int, float)) and
        isinstance(response_json["VAT_rate"], (int, float)) and
        isinstance(response_json["VAT_amount"], (int, float))):
        
        return True 
    else:
        return False


def valid_vat(response_json):
    if response_json["total_price"] == response_json["total_price_before_VAT"] == response_json["VAT_rate"] == response_json["VAT_amount"] == 0:
        return True

    vat_calc1 = (response_json["total_price"] / response_json["total_price_before_VAT"]) - 1
    vat_calc2 = response_json["VAT_amount"]/response_json["total_price_before_VAT"]
    extracted_vat = response_json["VAT_rate"] if response_json["VAT_rate"] < 1 else response_json["VAT_rate"] / 100
    indication = (round_and_compare(extracted_vat,vat_calc1) and round_and_compare(extracted_vat,vat_calc2))
    return indication
 
def valid_total_price(response_json):
    #indication = response_json["total_price"] == response_json["total_price_before_VAT"] + response_json["VAT_amount"]
    indication = round_and_compare(response_json["total_price"], response_json["total_price_before_VAT"] + response_json["VAT_amount"])

    return indication

def extract_valid_vat_dict(response_json, chatgpt_messages, model_name, client, additional_text='', max_attempts=5):
    attempt = 0
    #chatgpt_messages = []

    while attempt < max_attempts:
        if check_type(response_json) and valid_total_price(response_json) and valid_vat(response_json):
           return response_json
        else:     
           logger.info(f"Attempt: {attempt + 1} to extract the valid VAT. The current dictionary is: {repr(response_json)}")
           attempt += 1
           cur_content = f"The previous {attempt + 1} attempt to extract of the valid prices from the image into dictionary failed.\n" \
                         f"The previous result was: {repr(response_json)}\n" \
                         "Make sure that: 'total_price' = 'total_price_before_VAT' + 'VAT_amount' and 'VAT_rate' = 'VAT_amount' / 'total_price_before_VAT'\n" \
                         "Extract valid Python dictionary with no additional text, formatting, or code. The output should look exactly like this: {\"...\"}.\n" \
                         "Provide only the dictionary, nothing else.\n" + additional_text
            
           chatgpt_messages = prepare_chatgpt_msg(cur_content, chatgpt_messages)
           extraction_response = chatgpt_request_extraction(chatgpt_messages, model_name, client)
           response_text = extraction_response.choices[0].message.content
           response_json = extract_valid_dict(response_text, chatgpt_messages, OPENAI_MODEL, client)
    
    return None 
    # raise ValueError("Failed to extract correct values for JSON after multiple attempts.")

#IMAGE_PATH = "2.jpeg"  # Change this to your image path
#result = analyze_image(IMAGE_PATH, OPENAI_API_KEY)
#print(result)
