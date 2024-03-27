import csv
import os
import pprint
import random
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import (JsonOutputParser,
                                           PydanticOutputParser,
                                           StrOutputParser)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from openai import OpenAIError


def extract_link_metadata(link):
    try:
        response = requests.get(link, allow_redirects=True, timeout=20)
        response.raise_for_status()  # Raise exception for bad status codes
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract metadata such as title, description, etc.
        metadata = {
            'title': soup.title.string.strip() if soup.title else None,
            # Add more metadata fields as needed
        }
        
        return metadata
    except requests.exceptions.RequestException as e:
        print("Error fetching page:", e)
        return {}

def extract_links(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=20)
        response.raise_for_status()  # Raise exception for bad status codes
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
        
        #Extract links
        links = set()  # Using a set to avoid duplicate links
        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(url, link['href'])  # Make relative URLs absolute
            links.add(absolute_url)
        return list(links)
    except requests.exceptions.RequestException as e:
        print("Error fetching page:", e)
        return []

def analyze_food_menu_links(data):
    try:
        api_key = os.getenv("openai_api_key")
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125", openai_api_key=api_key)

        # Create a string output parser
        output_parser1 = StrOutputParser()

        # Create a chat prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a world class food menu link analyzer. Your job is to select the url links related to the restaurant food menu from {data}"),
            ("user", "{input}")
        ])

        class Menu_Links(BaseModel):
            url_link: str = Field(description="url link of the restaurant food related menu"),
            description: str = Field(description="provide with the reason why this link might be related to the restaurant menu")
        
        pyd_parser = PydanticOutputParser(pydantic_object=Menu_Links)

        # Define the prompt chain
        chain1 = prompt | llm | output_parser1

        # Invoke the chain with input data
        results = chain1.invoke({"input": "Please select the best links that could be related to the restaurant food menu from {data} and give description why it could be the link related to restaurant menu",
                             "data": data})
        # Return the results
        return results
    except OpenAIError as e:
        # Handle OpenAI API errors
        print(f"OpenAI API Error: {e}")
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred: {e}")

def main():
    input_path = r"C:\Users\shres\Desktop\Work\llm_practice1\files\Google_all_details.csv"
    output_path = r"C:\Users\shres\Desktop\Work\llm_practice1\files\final_data2.csv"
    
    df = pd.read_csv(input_path)
    res_urls = df['Website'][:7].tolist()

    df['menu_links'] = None
    df['sel_links'] = None

    # Ensure URLs start with "https://"
    res_urls = ['https://' + url if not url.startswith('http') else url for url in res_urls]
    pprint.pprint(res_urls)

    # Iterate over each URL, extract links, and update DataFrame
    for i, url in enumerate(res_urls):
        print(i)
        menu_links = extract_links(url)
        df.at[i, 'menu_links'] = menu_links
        data = ', '.join(menu_links)
        if data:
            # Call the function with your data
            analysis_results = analyze_food_menu_links(data)
            df.at[i, 'sel_links'] = analysis_results
        else:
            df.at[i, 'sel_links'] = []
            
    print(df['sel_links'])
    # Save the final DataFrame to a CSV file
    df_fin = df[:10]
    df_fin.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()
