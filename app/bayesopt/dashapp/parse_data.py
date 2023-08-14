import pandas as pd
import base64
import datetime
import io
from dash import dcc, html
from plotly import graph_objects as go
import torch
from .optimizer import Optimizer

class dataSizeException(Exception):
    pass

class tooManyParameters(Exception):
    pass

def parse(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    df = pd.read_csv(
    io.StringIO(decoded.decode('utf-8'))) 
    try:
        optimizer, figure = addToOptimizer(df)
    except dataSizeException:
        return html.Div([
            'Too many data points, must be less than or equal to 200'
        ]), "error"
    except tooManyParameters:
        return html.Div([
            'There were too many parameters in the input file'
        ]), "error"
    except Exception as e:
        print(e)    
        return html.Div([
            'There was an error processing the file'
        ]), "error"
    

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
        dcc.Dropdown(options = [{'label': 'Probability of Improvement', 'value': 'pi'}],  
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
        if len(y) > 200:
            raise dataSizeException
        optimizer = Optimizer(X, y)
        figure = go.Figure(go.Scatter(x = df["param1"], y = df["output"], mode = "markers", name = "Your Data"))
        figure.update_layout(xaxis_title = "param1", yaxis_title = "output")
        return optimizer, figure
    elif dimensions == 3:
        x1 = torch.tensor(df["param1"])
        x2 = torch.tensor(df["param2"])
        X = torch.cat((
            x1.contiguous().view(x1.numel(), 1),
            x2.contiguous().view(x2.numel(), 1)),
            dim=1
        )
        y = torch.tensor(df["output"])
        if len(y) > 200:
            raise dataSizeException
        optimizer = Optimizer(X, y)
        x1 = []
        x2 = []
        for item in X:
            x1.append(item[0].item())
            x2.append(item[1].item())
        figure = go.Figure(data = go.Scatter3d(x = x1, y = x2, z = y, mode = "markers", name = "Your Data"))
        figure.update_layout(scene = dict(
                    xaxis_title='param1',
                    yaxis_title='param2',
                    zaxis_title='output'),)
        return optimizer, figure
    else:
        raise Exception('error')
