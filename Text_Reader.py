import easyocr
import json
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

def OCR_Process(image_path):
    reader = easyocr.Reader(["en"],gpu=False)
    result = reader.readtext(image_path)
    ocr_text = "\n".join(i[1] for i in result)
    return ocr_text


def GPT_Bill_Cleaner(ocr_text, api_key):
    
    # === Setup API Client ===
    endpoint = "https://models.github.ai/inference"
    model = "openai/gpt-4.1"
    token = api_key

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token),
    )
    # === Prompt to instruct GPT ===
    user_prompt = f"""
    You are a bill parser and cleaner. From the OCR text below, do the following:
    - Correct any OCR or spelling errors if they are clearly wrong.
    - Extract the following details:
    - Restaurant name
    - GST number (if present)
    - Date
    - Items (each item should include name, quantity, and rate)
    - Tax amount (if present)
    - Total amount

    Return valid JSON only.

    OCR Text:
    {ocr_text}
    """

    # === Make API Call ===
    response = client.complete(
        messages=[
            SystemMessage("You are a bill parsing assistant."),
            UserMessage(user_prompt),
        ],
        temperature=0.3,
        top_p=1.0,
        model=model
    )

    # === Parse & Print the Response ===
    result = response.choices[0].message.content

    try:
        return json.loads(result) 
    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw": result}


