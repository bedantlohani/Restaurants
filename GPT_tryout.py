import csv
import json
import requests
import openai
import random


def fetch_menu_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Request error for {url}: {e}")
        return None


def process_content_with_openai(content):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system",
                 "content": "You are a world class food menu analyzer. Your job is to extract menu data from the given data."},
                {"role": "user", "content": f"Extract structured information from this restaurant menu: {content}"}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None


def read_csv_and_process_menus(csv_path):
    menus_info = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = list(csv.DictReader(csv_file))
            random_rows = random.sample(csv_reader, 10)  # Select 10 random records from the CSV

            for row in random_rows:
                menu_url = row.get('Menu URL')
                if not menu_url or not menu_url.startswith(('http://', 'https://')):
                    print(f"Invalid or missing URL in row: {row}")
                    continue

                menu_content = fetch_menu_content(menu_url)
                if menu_content:
                    processed_content = process_content_with_openai(menu_content)
                    if processed_content:

                        menus_info.append({
                            'url': menu_url,
                            'processed_content': processed_content  # Store raw string from API
                        })
                else:
                    print(f"Failed to fetch or process menu content from {menu_url}")
    except Exception as e:
        print(f"An error occurred while reading the CSV or processing menus: {e}")

    return menus_info


csv_path = "/Users/bedantlohani/PycharmProjects/DataWrangling/Rhode_Details_cleaned.csv"

try:
    menus_info = read_csv_and_process_menus(csv_path)
    print(json.dumps(menus_info, indent=4))
except Exception as e:
    print(f"An error occurred while processing: {e}")
