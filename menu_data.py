import csv
import requests
from PIL import Image
from io import BytesIO
from pytesseract import image_to_string

input_csv_path = 'menu_pic_info_cleaned.csv'
output_csv_path = 'menu_extract.csv'

def extract_text_from_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        text = image_to_string(image)
        return text
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"Other error occurred: {e}")
    return None

def process_csv(input_csv, output_csv):
    with open(input_csv, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['menu_extract']  # Append 'menu_extract' field
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            image_link = row['Image Link']
            row['menu_extract'] = extract_text_from_image(image_link) if image_link else ''
            writer.writerow(row)

process_csv(input_csv_path, output_csv_path)
