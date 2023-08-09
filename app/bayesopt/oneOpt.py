from flask import Flask, render_template, request, Blueprint
from . import config

blueprint = Blueprint('oneParam', __name__)

@blueprint.route('/singleparameter')
def singleParameter():
    return render_template("singleOpt.html")

@blueprint.route('/singleOptimization')
def singleOptimization():
    return "Single Optimization"

