
import csv
import requests
from bs4 import BeautifulSoup
import random
import json
from urllib.parse import urljoin
count = 0

def is_valid_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    if url.startswith("https://#") or "javascript:void(0);" in url or url.startswith("https://tel:") or "://" not in url:
        return False  # Filter out invalid URLs
    return url

def fetch_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()  # Will raise HTTPError for 4xx/5xx codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
    return None

def extract_links(html_content, parent_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # if is_valid_url(href):
        links.add(urljoin(parent_url, href))
    return links

def recursive_link_extraction(url, seen_urls=None, max_depth=3, current_depth=0):
    if seen_urls is None:
        seen_urls = set()
    if current_depth > max_depth or url in seen_urls:
        return seen_urls
    seen_urls.add(url)
    html_content = fetch_content(url)
    if html_content:
        links = extract_links(html_content, url)
        for link in links - seen_urls:
            recursive_link_extraction(link, seen_urls, max_depth, current_depth + 1)
    return seen_urls

def update_csv_with_links(csv_path, output_csv_path):
    with open(csv_path, mode='r', encoding='utf-8') as csv_file, \
         open(output_csv_path, 'w', newline='', encoding='utf-8') as output_file:

        csv_reader = list(csv.DictReader(csv_file))
        fieldnames = list(csv_reader[0].keys()) + ['Extracted Links']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        global count

        # sampled_records = random.sample(csv_reader, min(5, len(csv_reader)))
        for row in csv_reader:
            if count == 5:
                break
            count = count +1
            website_url = row.get('Website', '').strip()
            url_val = is_valid_url(website_url)
            if url_val:
                all_links = recursive_link_extraction(url_val)
                row['Extracted Links'] = json.dumps(list(all_links))
            else:
                row['Extracted Links'] = json.dumps([])
            writer.writerow(row)


csv_path = "/Users/bedantlohani/PycharmProjects/DataWrangling/Rhode_Details_cleaned.csv"
output_csv_path = "DataLaketry4.csv"

update_csv_with_links(csv_path, output_csv_path)
