import ast
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
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
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
                }
            ],
        )
        response_text = response.choices[0].message.content
        valid_text = extract_valid_dict(response_text, OPENAI_MODEL, client, additional_text='')
    
        return valid_text

def prepare_chatgpt_msg(text, chatgpt_messages):
    chatgpt_messages.append({"role": "user", "content": text})
    return chatgpt_messages

def chatgpt_request_extraction(msgs, model_name, client):
    response = client.chat.completions.create(model=model_name, messages=msgs)
    return response

def extract_valid_dict(response_text, model_name, client, additional_text='', max_attempts=5):
    attempt = 0
    chatgpt_messages = []

    while attempt < max_attempts:
        try:
            extracted_dict = ast.literal_eval(response_text)
            if isinstance(extracted_dict, dict):
                return extracted_dict
                
        except (SyntaxError, ValueError):
            logger.info(f"Attempt: {attempt + 1} to extract the Python dictionary from the text. The current dictionary is: {repr(response_text)}")
            attempt += 1
            prev_content = f"The previous {attempt + 1} attempt to extract of the valid Python dictionary from the text failed.\n" \
                            f"The previous result was: {response_text}\n" \
                            "Extract valid Python dictionary with no additional text, formatting, or code. The output should look exactly like this: {\"...\"}.\n" \
                            "Provide only the dictionary, nothing else.\n" + additional_text
            
            chatgpt_messages = prepare_chatgpt_msg(prev_content, chatgpt_messages)
            extraction_response = chatgpt_request_extraction(chatgpt_messages, model_name, client)
            response_text = extraction_response.choices[0].message.content
    
    raise ValueError("Failed to extract a valid Python list after multiple attempts.")


#IMAGE_PATH = "2.jpeg"  # Change this to your image path
#result = analyze_image(IMAGE_PATH, OPENAI_API_KEY)
#print(result)
