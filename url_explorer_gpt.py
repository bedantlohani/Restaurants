import csv
import requests
import openai
import re
import json
import random

def fetch_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def process_content_with_openai(content, prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def extract_menu_urls(ai_response):
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ai_response)
    return list(set(urls))

def update_records_with_menu_data(csv_path, output_csv_path):
    records = []
    with open(csv_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = list(csv.DictReader(csv_file))
        random.shuffle(csv_reader)

        processed_count = 0

        for row in csv_reader:
            if processed_count >= 5:
                break
            menu_url = row['Menu URL']
            if not menu_url or not menu_url.startswith(('http://', 'https://')):
                print(f"Invalid or missing URL in row: {row}")
                continue
            if menu_url:
                content = fetch_content(menu_url)
                if content:
                    prompt = """
        Analyze the provided HTML content or website description and extract structured menu information. 
        If the page does not contain direct menu information but links to menu pages, list those links with descriptions
        . Provide structured data in JSON format including categories like 'Appetizers', 'Main Courses', 'Desserts', 
        with items, prices, and descriptions. If direct menu information is unavailable, list the URLs to menu pages 
        along with a brief description of each link.
        """
                    ai_response = process_content_with_openai(content, prompt)
                    additional_urls = extract_menu_urls(ai_response)
                    menu_data = []
                    for url in additional_urls:
                        page_content = fetch_content(url)
                        if page_content:
                            menu_prompt = """
        Analyze the provided HTML content or website description and extract structured menu information. 
         Provide structured data in JSON format including categories like 'Appetizers', 'Main Courses', 'Desserts', 
        with items, prices, and descriptions. If direct menu information is unavailable, list the URLs to menu pages 
        along with a brief description of each link.
        """
                            page_menu_data = process_content_with_openai(page_content, menu_prompt)
                            menu_data.append({'url': url, 'data': page_menu_data})
                    row['Menu Data'] = json.dumps(menu_data)
            records.append(row)
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

csv_path = "/Users/bedantlohani/PycharmProjects/DataWrangling/Rhode_Details_cleaned.csv"
output_csv_path = "menu_gpt_try2.csv"

try:
    update_records_with_menu_data(csv_path, output_csv_path)
    print("Menu data processing is complete. Check the output CSV file for results.")
except Exception as e:
    print(f"An error occurred while processing: {e}")
