import json
from DocScanner import DocScanner
import Text_Reader as TR

def Main_DocScanner(image_path):
    """
    Scans a single image.

    Args:
        image_path (str): Path to the image to be scanned.
    """
    scanner = DocScanner()
    final = scanner.scan(image_path)

    ocrText = TR.OCR_Process(final)
    api_key = input("Enter Your Key:")
    cleaned_data = TR.GPT_Bill_Cleaner(ocrText, api_key)

    if "error" in cleaned_data:
        print("⚠️ GPT response could not be parsed as JSON:")
        print(cleaned_data["raw"])   # show raw GPT output
    else:
        print("✅ Structured Bill:")
        print(json.dumps(cleaned_data, indent=2))


Main_DocScanner("/input/bill8.jpg")

