import os
import pandas as pd

project_directory = '/Users/bedantlohani/PycharmProjects/DataWrangling'

# Keywords that might indicate a non-restaurant
non_operator_keywords = ['clothing', 'apparel', 'store', 'stop', 'boutique', 'retail', 'cleaning', 'office', 'commercial',
                         'wholesale']

fields_to_check = {
    'Type_of_Restaurant': True,
    'Description': True,
    'Facilities': True,
    'Menu': True,
    'Listing_URL': True,  # Assuming URLs are likely to contain useful keywords
    'Name': True
}


def filter_file(df):
    for column, is_text in fields_to_check.items():
        if column in df.columns and is_text:
            # Safely convert column to string to avoid issues with different data types
            df[column] = df[column].astype(str)
            for keyword in non_operator_keywords:
                df = df[~df[column].str.contains(keyword, case=False, na=False)]
    return df


def process_files(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if not file_path.endswith('.csv'):
            continue  # Skip non-CSV/XLSX files

        print(f"Processing {filename}...")
        try:
            # Read file based on its extension
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:  # .xlsx
                df = pd.read_excel(file_path)

            # Filter non-operator data
            df_cleaned = filter_file(df)

            # Save cleaned data back to CSV (even if originally XLSX for uniformity)
            cleaned_path = os.path.splitext(file_path)[0] + '_cleaned.csv'
            df_cleaned.to_csv(cleaned_path, index=False)
            print(f"Cleaned data saved to {cleaned_path}")

        except Exception as e:
            print(f"Failed to process {filename}: {e}")


# Run the process
process_files(project_directory)
