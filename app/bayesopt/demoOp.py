from flask import Flask, render_template, request, Blueprint
from . import config

blueprint = Blueprint('demo', __name__)

@blueprint.route('/demo')
def demo():
    return render_template("demo.html")

@blueprint.route("/demoOptimization")
def demoOptimization():
    return "demo optimization" 