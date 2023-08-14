from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import plotly.graph_objects as go
import plotly.express as px
import base64
import datetime
import io
import pandas as pd
import torch
from .parse_data import parse 
from . import config

external_stylesheets = ["../static/styles/dashApp.css"]

def create_dash_app(flaskApp):
    dashApp = Dash(__name__, server = flaskApp, url_base_pathname = "/dash/", external_stylesheets = external_stylesheets)

    #upload data button
    dashApp.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'font-color': 'white'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='output-data-upload'),
    html.Div(id='output-optimize'),
    html.Div(style = {'height': '50px'})
    ])    
    
    return dashApp

####

@callback(Output('output-data-upload', 'children'),
            Input('upload-data', 'contents'),
            State('upload-data', 'filename'))
def updateOutput(content, filename):
    if content is not None:
        children, config.optimizer = parse(content, filename)
        children = [children]
        return children
    
@callback(Output('output-optimize', 'children'),
          Input('submit-button', 'n_clicks'),
          State('dropdown-button', 'value'),
          State('kernel-dropdown', 'value'),
          State('aq-dropdown', 'value'))
def optimize(n_clicks, optimizationTarget, kernel, acquisition):
    if n_clicks:
        n_clicks = 0
        config.optimizer.setOptimizationTarget(optimizationTarget)
        config.optimizer.setKernel(kernel)
        config.optimizer.setAcquisition(acquisition)
        config.optimizer.run() 
        # try:
        # except Exception as e:
        #     print(e)
        #     return html.Div([
        #         'There was an error running the optimization'
        #     ])
        figure = config.optimizer.plot()
        result = config.optimizer.result()
        return html.Div([
            html.H5("Optimization results: "),
            html.P(result),
            dcc.Graph(
                figure = figure,
                style = {
                    'width': '80%',
                    'margin': 'auto',
                    'align-items': 'center'
                }
            )
            ])
