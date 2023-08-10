from flask import Flask, render_template, request, Blueprint
from . import config
from .dashapp import upload
import dash

blueprint = Blueprint('oneParam', __name__)

@blueprint.route('/singleparameter')
def singleParameter():
    return render_template("singleOpt.html")

@blueprint.route('/singleOptimization')
def singleOptimization():
    dashApp = upload.create_dash_app(config.app)
    return dash.init_app(app = dashApp)

