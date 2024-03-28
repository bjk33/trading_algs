# Tying it all together:
# create a refinitiv connection
# request data based on USER INPUT
# get data
# process it into something
# update it as a live webpage!!! :)

import dash
import plotly.graph_objects as go
from dash import dcc, html
import refinitiv.dataplatform.eikon as ek
import os
from dotenv import load_dotenv

load_dotenv('/Users/brandonkaplan/Desktop/FINTECH533/.env')
app_key = os.getenv('EIKON_API_KEY')

ek.set_app_key(app_key)

# Create a Dash app
app = dash.Dash(__name__)

# Create the page layout
app.layout = html.Div([
    # Identifier for what asset to fetch from Bloomberg (IVV US Equity)
    dcc.Input(id='identifier', type="text", value="AAPL.O"),
    dcc.Input(id='N', type="number", value="365"),
    ############################################################################
    ############################################################################
    # Display the current selected date range
    html.Button("QUERY REFINITIV", id='query-refinitiv', n_clicks=0),
    dcc.Graph(
        id='candlestick',
        style={'display': 'none'}),
    html.Div(id='date-range-output', children=[]),
])


@app.callback(
    #### update the figure!
    [dash.dependencies.Output('candlestick', 'figure'),
     dash.dependencies.Output('candlestick', 'style'),
     dash.dependencies.Output("date-range-output", "children"),
     ],
    dash.dependencies.Input("query-refinitiv", 'n_clicks'),
    [dash.dependencies.State("identifier", "value"),
     dash.dependencies.State('N', 'value')],
    prevent_initial_call=True
)
def update_bbg_data(nclicks, identifier, N):
    historical_data = ek.get_data(
        instruments=[identifier],
        fields=[
            'TR.OPENPRICE',
            'TR.HIGHPRICE',
            'TR.LOWPRICE',
            'TR.CLOSEPRICE',
            'TR.CLOSEPRICE.DATE'
        ],
        parameters={
            'SDate': '0',
            'EDate': "-" + str(N),
            'Frq': 'D',
            'CH': 'IN;Fd',
            'RH': 'date'
        },
    )

    print(historical_data[0]["Date"])

    max_date = historical_data[0]["Date"].max()
    min_date = historical_data[0]["Date"].min()
    print(historical_data)
    print(max_date[:10])
    print(min_date[:10])
    out_date = min_date[:10] + " to " + max_date[:10]

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=historical_data[0]["Date"],
                open=historical_data[0]["Open Price"],
                high=historical_data[0]["High Price"],
                low=historical_data[0]["Low Price"],
                close=historical_data[0]["Close Price"],
            )
        ]
    )

    return fig, {'display': 'block'}, out_date


# Run it!
if __name__ == '__main__':
    app.run_server(debug=True)
