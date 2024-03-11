import pandas as pd

xlsx_file = 'locmatic_yelp_com_reviews_20240301.xlsx'
csv_file = 'yelp_reviews.csv'

df = pd.read_excel(xlsx_file)

df.to_csv(csv_file, index=False)
