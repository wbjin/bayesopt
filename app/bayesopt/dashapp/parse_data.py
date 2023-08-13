import pandas as pd
import base64
import datetime
import io
from dash import dcc, html
from plotly import graph_objects as go
import torch
from .optimizer import Optimizer

def parse(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        df = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    
    try:
        optimizer = addToOptimizer(df)
    except Exception as e:
        return html.Div([
            'There was an error processing this file.'
        ]) 
    
    figure = go.Figure(go.Scatter(x = df["param1"], y = df["output"], mode = "markers", name = "Your Data"))

    return html.Div([
        html.H5(filename),
        html.H5("Your data"),

        dcc.Graph(
            figure = figure,
            style = {
                    'width': '80%',
                    'margin': 'auto',
                    'align-items': 'center'
                }
        ),
        html.Hr(),  # horizontal line
        html.Div([
        dcc.Dropdown(["Maximize", "Minimize"], 
                     id ='dropdown-button',
                     placeholder = "Choose optimization objective",
                     searchable = False,
                     style = {
                         'width': '60%',
                         'text-align': 'center',
                         'color': 'black',
                         'margin': 'auto',
                         'font-family': "ff-meta-serif-web-pro, serif"
                     }),
        dcc.Dropdown(
                    options = [{'label': 'Matern 5/2', 'value': 'matern'},
                               {'label': 'Squared Exponential', 'value': 'sek'}], 
                     id ='kernel-dropdown',
                        placeholder = "Choose kernel",
                     searchable = False,
                     style = {
                         'width': '60%',
                         'text-align': 'center',
                         'color': 'black',
                         'margin': '10px',
                         'margin': 'auto',
                         'font-family': "ff-meta-serif-web-pro, serif"
                     }),
        dcc.Dropdown(options = [{'label': 'Probability of Improvement', 'value': 'pi'},
                               {'label': 'Expected Improvement', 'value': 'ei'}],  
                     id ='aq-dropdown',
                     placeholder = "Choose acquisition function",
                     searchable = False,
                     style = {
                         'width': '60%',
                         'text-align': 'center',
                         'color': 'black',
                         'margin': '10px',
                         'margin': 'auto',
                         'font-family': "ff-meta-serif-web-pro, serif"
                     }),
        html.Button(id = "submit-button", 
                    n_clicks = 0, 
                    children = "Submit", 
                    style = {
                        'background-color': 'white',
                        'color': 'black',
                        'margin': '10px',
                        'font-family': "ff-meta-serif-web-pro, serif"
                    }),
        ],
        style = {
            'align-items': 'center'
        })

    ]), optimizer

def addToOptimizer(df):
    dimensions = len(df.columns)
    if dimensions == 2:
        X = torch.tensor(df["param1"])
        y = torch.tensor(df["output"])
        optimizer = Optimizer(X, y)
        return optimizer
    else:
        raise Exception('error')
