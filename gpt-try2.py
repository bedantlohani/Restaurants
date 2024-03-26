import csv
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
                 "content": "You are a sophisticated menu analysis tool. Extract structured menu information including categories, subcategories, items, descriptions, prices, and images."},
                {"role": "user", "content": content}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None


def read_csv_and_process_menus(csv_path, output_csv_path):
    with open(csv_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = list(csv.DictReader(csv_file))
        random.shuffle(csv_reader)

    processed_count = 0
    menus_info = []

    for row in csv_reader:
        if processed_count >= 10:
            break

        menu_url = row.get('Menu URL')
        if not menu_url or not menu_url.startswith(('http://', 'https://')):
            print(f"Invalid or missing URL in row: {row}")
            continue

        menu_content = fetch_menu_content(menu_url)
        if menu_content:
            processed_content = process_content_with_openai(menu_content)
            if processed_content:
                menus_info.append({
                    **row,
                    'Menu Data': processed_content
                })
                processed_count += 1
        else:
            print(f"Failed to fetch or process menu content from {menu_url}")


    if menus_info:
        fieldnames = menus_info[0].keys()
        with open(output_csv_path, mode='w', newline='', encoding='utf-8') as output_file:
            csv_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            for info in menus_info:
                csv_writer.writerow(info)


csv_path = "/Users/bedantlohani/PycharmProjects/DataWrangling/Rhode_Details_cleaned.csv"
output_csv_path = "menu_gpt_try.csv"

try:
    read_csv_and_process_menus(csv_path, output_csv_path)
    print("Menu data processing is complete. Check the output CSV file for results.")
except Exception as e:
    print(f"An error occurred while processing: {e}")
