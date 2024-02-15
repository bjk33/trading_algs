import pandas as pd
import os
from dotenv import load_dotenv
import refinitiv.dataplatform.eikon as ek
import plotly.graph_objects as go
from datetime import datetime

load_dotenv('/Users/brandonkaplan/Desktop/FINTECH533/.env')
api_key = os.getenv('EIKON_API_KEY')
ek.set_app_key(api_key)

data_tuple = ek.get_data(
    instruments = ['NVDA.O'],
    fields=[
        'TR.OPENPRICE',
        'TR.HIGHPRICE',
        'TR.LOWPRICE',
        'TR.CLOSEPRICE',
        'TR.CLOSEPRICE.DATE'
    ],
    parameters={
        'SDate': '2023-02-15',
        'EDate': '2024-02-15',
        'Curn': 'USD'
    }
)
df = data_tuple[0]
print(df)

fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['Open Price'],
                high=df['High Price'],
                low=df['Low Price'],
                close=df['Close Price'])])

fig.show()



