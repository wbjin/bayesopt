from flask import Flask, render_template, request, Blueprint
from . import config

blueprint = Blueprint('threeParam', __name__)

@blueprint.route('/threeparameter')
def singleParameter():
    return render_template("threeOpt.html")

@blueprint.route('/threeOptimization')
def singleOptimization():
    return "Three Parameter Optimization"