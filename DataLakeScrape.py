import csv
import requests
from bs4 import BeautifulSoup
import random
import json

def is_valid_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    if url.startswith("https://#") or "javascript:void(0);" in url or url.startswith("https://tel:") or "://" not in url:
        return False  # Filter out invalid URLs
    return url

def fetch_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
    return ""

def extract_links(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()

    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/'):
            href = base_url + href
        href = is_valid_url(href)
        if href:
            links.add(href)

    return links

def recursive_link_extraction(url, seen_urls=set(), max_depth=2, current_depth=0):
    if current_depth > max_depth or url in seen_urls or not url:
        return seen_urls
    seen_urls.add(url)
    html_content = fetch_content(url)
    if html_content:
        links = extract_links(html_content, url)
        for link in links:
            if link not in seen_urls:
                seen_urls = recursive_link_extraction(link, seen_urls, max_depth, current_depth+1)
    return seen_urls

def update_csv_with_links(csv_path, output_csv_path):
    updated_records = []
    with open(csv_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = list(csv.DictReader(csv_file))
        sampled_records = random.sample(csv_reader, min(5, len(csv_reader)))

        for row in sampled_records:
            website_url = row.get('Website', '')
            website_url = is_valid_url(website_url)
            if website_url:
                all_links = recursive_link_extraction(website_url)
                row['Extracted Links'] = json.dumps(list(all_links))
                updated_records.append(row)

    fieldnames = list(csv_reader[0].keys()) + ['Extracted Links']
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for record in updated_records:
            writer.writerow(record)

csv_path = "/Users/bedantlohani/PycharmProjects/DataWrangling/Rhode_Details_cleaned.csv"
output_csv_path = "DataLaketry2.csv"

update_csv_with_links(csv_path, output_csv_path)
