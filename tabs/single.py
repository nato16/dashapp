import dash
import requests
import json
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import time
import dash_table
import os

def get_stock(symbol,interval):
    proxies={}
    api_url = 'http://api:8000/stock/get'
    req_url = '/'.join([api_url, symbol, interval])
    response = requests.get(req_url, verify=False, proxies=proxies)
    return response.json()

def get_options():
    proxies={}
    api_url = 'http://api:8000/stocks/'
    response = requests.get(api_url,verify=False, proxies=proxies)
    return response.json()

stocks=get_options()


single_layout = html.Div(children=[
    html.H1(children='M0'),
    html.Div([
        html.Div([
            #dcc.Input(id='stock-abv', type='text')
            dcc.Dropdown(
                id='stock-abv',
                options=stocks,
                )
            ],style={'width':'30%','display':'table-cell',}),
        html.Div([
            html.Button(id='submit-button', n_clicks=0, children='Show Data')
        ],style={'witdh':'5%','display':'table-cell'}),
        html.Div([
            html.Button(id='update-stock',n_clicks=0,children='Update Data')
        ],style={'witdh':'5%','display':'table-cell'}),
    ],style={'width':'40%','display':'table'}),
    html.Div([
        dcc.ConfirmDialog(
            id='confirm-success',
            message='Data successfully inserted',
        )
    ]),
    html.Hr(),
    html.Div([
        dcc.Graph(
            id='stock-graph-daily',
            figure={}),
        dcc.Graph(
            id='stock-graph-daily-vol',
            figure={})    
        ],
        style={'width': '49%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(
            id='stock-graph-weekly',
            figure={}
        ),
        dcc.Graph(
            id='stock-graph-weekly-vol',
            figure={}
        )],
        style={'width': '49%', 'display': 'inline-block'})
])


def callback_update_graph(app):
	@app.callback(
		[Output('stock-graph-daily', 'figure'),
		Output('stock-graph-daily-vol', 'figure'),
		Output('stock-graph-weekly','figure'),
		Output('stock-graph-weekly-vol','figure'),
		],
		[Input('submit-button', 'n_clicks')],
		[State('stock-abv','value')]
	)
	def update_graph(n_clicks, input_value):
		if n_clicks==0:
		    return [{},{},{},{}]
		
		intervals={'Last 100 days':'TIME_SERIES_DAILY',
		        'Last 20 years in Week':'TIME_SERIES_WEEKLY'}

		figures=[]
		for title,interval in intervals.items():
		    data_json=get_stock(input_value,interval)
		    data_df=pd.DataFrame.from_records(data_json,columns=["date","open","high","low","close","volume"])
		
		    traces=[]
		    for coln in data_df.columns[1:-1]:
		        if title=='Intraday':
		            x=list(data_df.index)
		        else:
		            x=list(data_df['date'])
		        traces.append(dict(
		            mode='lines',
		            y=list(data_df[coln]),
		            x=x,
		            name=coln
		        ))
		
		    figure={
		        'data': traces,
		        'layout': dict(
		            title=title,
		            xaxis={'title': 'Date'},
		            yaxis={'title': 'Value'}
		            )
		        }
		    figure_vol={
		        'data':[dict(type='bar',x=x,y=list(data_df["volume"]))],
		        'layout':dict(
		            xaxis={'type':'Date'},
		            yaxis={'title':'Volume'}
		        )
		    }
		    figures.append(figure)
		    figures.append(figure_vol)
		return figures

def callback_display_confirm(app):
	@app.callback(
		Output('confirm-success', 'displayed'),
		[Input('update-stock', 'n_clicks')],
		[State('stock-abv','value')]
	)
	def display_confirm(n_clicks,input_value):
		intervals={'Last 100 days':'TIME_SERIES_DAILY',
		        'Last 20 years in Week':'TIME_SERIES_WEEKLY'}
		if n_clicks>0:
		    api_url = 'http://api:8000/stock/post'
		    for title, interval in intervals.items():
		        req_url = '/'.join([api_url, input_value, interval,os.environ.get('mykey')])
		        response = requests.post(req_url, verify=False)
		    return True
		return False



if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port='8050')
