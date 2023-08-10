import os
from flask import Flask, render_template, request
from . import config
from . import demoOp
from . import oneOpt
from . import twoOpt
from . import threeOpt
from . import fourOpt
from .dashapp import upload
from dash import Dash

def createApp():
    app = config.app
    upload.create_dash_app(app)

    app.register_blueprint(demoOp.blueprint)
    app.register_blueprint(oneOpt.blueprint)
    app.register_blueprint(twoOpt.blueprint)
    app.register_blueprint(threeOpt.blueprint)
    app.register_blueprint(fourOpt.blueprint) 

    return app

app = createApp()

@app.route('/')
def index():
    return render_template("index.html")


