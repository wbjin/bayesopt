from flask import Flask, render_template, request, Blueprint
from . import config

blueprint = Blueprint('fourParam', __name__)

@blueprint.route('/fourparameter')
def singleParameter():
    return render_template("fourOpt.html")

@blueprint.route('/fourOptimization')
def singleOptimization():
    return "Four Parameter Optimization"