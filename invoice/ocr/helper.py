import base64
from openai import OpenAI
from logger import logger
def get_openai_client(openai_api_key):
    """Initialize and return OpenAI client with API key."""
    if not openai_api_key:
        raise ValueError("APi key not found. Ensure it's set in the .env file.")
    return OpenAI(api_key=openai_api_key)

def encode_image(image):
    """Read and encode an image to Base64 format."""
    try:
        return base64.b64encode(image).decode("utf-8")
    except Exception as e:
        logger.error(f"Error encoding image: {e}")
        return None