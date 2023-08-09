import os
from flask import Flask, render_template, request
from . import config
from . import demoOp
from . import oneOpt
from . import twoOpt
from . import threeOpt
from . import fourOpt

app = config.app
app.register_blueprint(demoOp.blueprint)
app.register_blueprint(oneOpt.blueprint)
app.register_blueprint(twoOpt.blueprint)
app.register_blueprint(threeOpt.blueprint)
app.register_blueprint(fourOpt.blueprint)

@app.route('/')
def index():
    return render_template("index.html")



