import csv
import re
import json

# regex patterns
item_pattern = r'(?P<name>.+?)\.{3,}\s*\$(?P<price>\d+\.\d{2})'
section_pattern = r'(?P<section>[A-Za-z\s]+)\n\n(?P<items>[^\n]+(?:\n(?!\n)[^\n]+)*)'


def extract_items(section_text):
    items = []
    for match in re.finditer(item_pattern, section_text, re.DOTALL):
        items.append({
            "Item Name": match.group('name').strip(),
            "Item Price": match.group('price'),
            "Item Description": ""
        })
    return items


def parse_menu(menu_text):
    sections = {}
    for match in re.finditer(section_pattern, menu_text):
        section_name = match.group('section').strip()
        section_items = match.group('items').strip()
        sections[section_name] = extract_items(section_items)
    return sections


input_csv_path = 'menu_extract.csv'
output_csv_path = 'menu_extract_regex.json'

with open(input_csv_path, mode='r', newline='', encoding='utf-8') as infile, \
        open(output_csv_path, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    for row in reader:
        menu_text = row['menu_extract'].replace('"', '')
        structured_menu = parse_menu(menu_text)
        row['structured_menu'] = json.dumps(structured_menu, indent=4)
        outfile.write(f'{row["structured_menu"]}\n\n')
