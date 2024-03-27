import csv
import requests
import openai
from bs4 import BeautifulSoup
import random


def fetch_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def extract_links(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    links = [a.get('href') for a in soup.find_all('a', href=True)]
    return [link for link in links if link.startswith('http')]

def process_content_with_openai(content, prompt):
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt + "\n\n" + content,
            temperature=0.5,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def filter_menu_urls(urls):
    prompt = "Identify which of these URLs are most likely to contain a restaurant's menu (and menu data only so disregard any " \
             "url that is unlikely to contain information ab out the restaurant's menu and only retai  the links that are " \
             "very likely to contain information about the menu specifically" \
             " and provide a brief description for each. i absoliutely do not need the links that are irrelevant to data" \
             "directly related to the menu of the restaurants" \
             "so do not include them in your final response"
    content = "\n".join(urls)
    return process_content_with_openai(content, prompt)

def update_records_with_menu_data(csv_path, output_csv_path):
    records = []
    with open(csv_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = list(csv.DictReader(csv_file))
        random.shuffle(csv_reader)

    valid_records_processed = 0
    for row in csv_reader:
        if valid_records_processed >= 5:
            break
        menu_url = row.get('Menu URL', '')
        if not menu_url.startswith('http'):
            continue
        content = fetch_content(menu_url)
        if content:
            all_links = extract_links(content)
            relevant_links_desc = filter_menu_urls(all_links)
            row['Links Extracted'] = relevant_links_desc
            records.append(row)
            valid_records_processed += 1

    fieldnames = csv_reader[0].keys() | {'Links Extracted'}
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record)

csv_path = "/Users/bedantlohani/PycharmProjects/DataWrangling/Rhode_Details_cleaned.csv"
output_csv_path = "menu_gpt_try3.csv"

try:
    update_records_with_menu_data(csv_path, output_csv_path)
    print("CSV file has been updated. Check the output CSV file for results.")
except Exception as e:
    print(f"An error occurred while processing: {e}")
