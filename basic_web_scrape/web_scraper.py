import requests
from bs4 import BeautifulSoup
import pandas as pd
import lxml
import html5lib
from io import StringIO
import os

YYYY = 2024

URL = 'https://home.treasury.gov/resource-center/data-chart-center/' + \
       'interest-rates/TextView?type=' + \
      'daily_treasury_yield_curve&field_tdr_date_value=' + str(YYYY)

cmt_rates_page = requests.get(URL)

soup = BeautifulSoup(cmt_rates_page.content, 'html5lib')
soup.find('table', {'class': 'views-table'})

# We want to access the table with the daily treasury par yield curve rates

df = pd.read_html(StringIO(str(soup.find('table', {'class': 'views-table'}))))[0]
yield_df = df.drop(df.columns[1:10], axis=1)
