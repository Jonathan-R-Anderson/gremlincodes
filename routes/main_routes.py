from flask import Blueprint, render_template, jsonify, request
from shared import gremlinThreadContract, gremlinDAOContract
from shared import gremlinDAOABI, gremlinThreadABI, gremlinPostABI, sysAdminContractABI, posterABI
from shared import gremlinDAOAddress, gremlinThreadAddress, gremlinPostAddress, sysAdminContractAddress, posterAddress
from shared import app

main_bp = Blueprint('main', __name__)

@app.route('/')
def index():
    return render_template(
        'index.html',
        gremlinDAOABI=gremlinDAOABI,
        gremlinThreadABI=gremlinThreadABI,
        gremlinPostABI=gremlinPostABI,
        sysAdminContractABI=sysAdminContractABI,
        posterABI=posterABI,
        gremlinDAOAddress=gremlinDAOAddress,
        gremlinThreadAddress=gremlinThreadAddress,
        gremlinPostAddress=gremlinPostAddress,
        sysAdminContractAddress=sysAdminContractAddress,
        posterAddress=posterAddress
    )

@app.route('/contract_data')
def contract_data():
    data = {
        'gremlinDAOABI': gremlinDAOABI,
        'gremlinThreadABI': gremlinThreadABI,
        'gremlinPostABI': gremlinPostABI,
        'sysAdminContractABI': sysAdminContractABI,
        'posterABI': posterABI,
        'gremlinDAOAddress': gremlinDAOAddress,
        'gremlinThreadAddress': gremlinThreadAddress,
        'gremlinPostAddress': gremlinPostAddress,
        'sysAdminContractAddress': sysAdminContractAddress,
        'posterAddress': posterAddress
    }
    return jsonify(data)

@main_bp.route('/sysadmin')
def sysadmin():
    return render_template('sysadmin.html')

@main_bp.route('/dao_control')
def dao_control():
    return render_template('dao_control.html')

@main_bp.route('/search_tags')
def search_tags():
    query = request.args.get('q', '')
    tags = []

    # Fetch tags from the smart contract
    total_tags = gremlinDAOContract.functions.getAllTags().call()
    for tag in total_tags:
        if query.lower() in tag['name'].lower():
            tags.append(tag['name'])

    return jsonify(tags)
