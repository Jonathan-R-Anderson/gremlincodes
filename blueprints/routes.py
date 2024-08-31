from flask import Blueprint, render_template
from shared import gremlinThreadABI, gremlinThreadAddress
import json

blueprint = Blueprint('blueprint', __name__)

@blueprint.route('/')
def index():
    return render_template('index.html', gremlinThreadABI=json.dumps(gremlinThreadABI[0]), gremlinThreadAddress=gremlinThreadAddress)