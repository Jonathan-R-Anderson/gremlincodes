from flask import Blueprint, render_template
from shared import gremlinThreadABI, gremlinThreadAddress, gremlinAdminABI, gremlinAdminAddress, gremlinReplyABI, gremlinReplyAddress
import json

blueprint = Blueprint('blueprint', __name__)

@blueprint.route('/')
def index():
    return render_template('index.html', 
                           gremlinThreadABI=json.dumps(gremlinThreadABI, ensure_ascii=False),  # Avoid ASCII escaping
                           gremlinThreadAddress=gremlinThreadAddress,
                           gremlinAdminABI=json.dumps(gremlinAdminABI, ensure_ascii=False),  # Avoid ASCII escaping
                           gremlinAdminAddress=gremlinAdminAddress,
                           gremlinReplyABI=json.dumps(gremlinReplyABI, ensure_ascii=False),
                           gremlinReplyAddress=gremlinReplyAddress)
