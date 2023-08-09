from flask import Flask, render_template, request, Blueprint
from . import config

blueprint = Blueprint('twoParam', __name__)

@blueprint.route('/twoparameter')
def singleParameter():
    return render_template("twoOpt.html")

@blueprint.route('/twoOptimization')
def singleOptimization():
    return "Two Parameter Optimization"
