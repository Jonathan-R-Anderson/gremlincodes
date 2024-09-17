import os
import random
import ipaddress
from pathlib import Path
from flask import Flask
from flask_restful import Api
from werkzeug.datastructures import ImmutableDict
from web3 import Web3
from web3.exceptions import ContractLogicError
import json

class ManiwaniApp(Flask):
    jinja_options = ImmutableDict()

app = ManiwaniApp(__name__, static_url_path='')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["UPLOAD_FOLDER"] = Path("./uploads").resolve()
app.config["THUMB_FOLDER"] = Path(os.path.join(app.config["UPLOAD_FOLDER"], "thumbs")).resolve()
app.config["SERVE_STATIC"] = True
app.config["SERVE_REST"] = True
app.config["USE_RECAPTCHA"] = False
app.config["FIREHOSE_LENGTH"] = 10

if os.getenv("MANIWANI_CFG"):
    app.config.from_envvar("MANIWANI_CFG")
    
app.url_map.strict_slashes = False
rest_api = Api(app)

# Web3 connection to zkSync Era mainnet
#web3 = Web3(Web3.HTTPProvider('https://endpoints.omniatech.io/v1/zksync-era/mainnet/1a6a3c9fbe4c40d5b4d6c46b466e674f'))

# Contract addresses
gremlinThreadAddress = '0x7aA9305b453Cd5Ad1C6dDcaEbb14Af9febB83199'
gremlinAdminAddress = '0x69B0C4FDAC564C8DC5Eb64e9cAFe691f4af6BF94'

# Contract ABIs
gremlinThreadABI = [json.loads(
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": False,
      "inputs": [
        {"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"}
      ],
      "name": "ThreadBlacklisted",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "parentThreadId",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "subject",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "email",
          "type": "string"
        }
      ],
      "name": "ThreadCreated",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"}
      ],
      "name": "ThreadWhitelisted",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "admin",
      "outputs": [
        {"internalType": "address", "name": "", "type": "address"}
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {"internalType": "address", "name": "_addr", "type": "address"}
      ],
      "name": "banAddress",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {"internalType": "address", "name": "", "type": "address"}
      ],
      "name": "bannedAddresses",
      "outputs": [
        {"internalType": "bool", "name": "", "type": "bool"}
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {"internalType": "uint256", "name": "_threadId", "type": "uint256"}
      ],
      "name": "blacklistThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_subject",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_email",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_magnetUrl",
          "type": "string"
        },
        {
          "internalType": "string[]",
          "name": "_tags",
          "type": "string[]"
        },
        {
          "internalType": "string",
          "name": "_content",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "_parentThreadId",
          "type": "uint256"
        }
      ],
      "name": "createThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getAllThreads",
      "outputs": [
        {
          "components": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "string", "name": "subject", "type": "string"},
            {"internalType": "string", "name": "email", "type": "string"},
            {"internalType": "string", "name": "magnetUrl", "type": "string"},
            {"internalType": "string[]", "name": "tags", "type": "string[]"},
            {"internalType": "string", "name": "content", "type": "string"},
            {"internalType": "uint256", "name": "parentThreadId", "type": "uint256"},
            {"internalType": "address", "name": "sender", "type": "address"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "bool", "name": "whitelisted", "type": "bool"},
            {"internalType": "bool", "name": "blacklisted", "type": "bool"}
          ],
          "internalType": "struct GremlinThread.Thread[]",
          "name": "",
          "type": "tuple[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {"internalType": "uint256", "name": "_threadId", "type": "uint256"}
      ],
      "name": "getThread",
      "outputs": [
        {
          "components": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "string", "name": "subject", "type": "string"},
            {"internalType": "string", "name": "email", "type": "string"},
            {"internalType": "string", "name": "magnetUrl", "type": "string"},
            {"internalType": "string[]", "name": "tags", "type": "string[]"},
            {"internalType": "string", "name": "content", "type": "string"},
            {"internalType": "uint256", "name": "parentThreadId", "type": "uint256"},
            {"internalType": "address", "name": "sender", "type": "address"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "bool", "name": "whitelisted", "type": "bool"},
            {"internalType": "bool", "name": "blacklisted", "type": "bool"}
          ],
          "internalType": "struct GremlinThread.Thread",
          "name": "",
          "type": "tuple"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "threadCount",
      "outputs": [
        {"internalType": "uint256", "name": "", "type": "uint256"}
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {"internalType": "uint256", "name": "", "type": "uint256"}
      ],
      "name": "threads",
      "outputs": [
        {"internalType": "uint256", "name": "id", "type": "uint256"},
        {"internalType": "string", "name": "name", "type": "string"},
        {"internalType": "string", "name": "subject", "type": "string"},
        {"internalType": "string", "name": "email", "type": "string"},
        {"internalType": "string", "name": "magnetUrl", "type": "string"},
        {"internalType": "string", "name": "content", "type": "string"},
        {"internalType": "uint256", "name": "parentThreadId", "type": "uint256"},
        {"internalType": "address", "name": "sender", "type": "address"},
        {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
        {"internalType": "bool", "name": "whitelisted", "type": "bool"},
        {"internalType": "bool", "name": "blacklisted", "type": "bool"}
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {"internalType": "address", "name": "newAdmin", "type": "address"}
      ],
      "name": "transferAdmin",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {"internalType": "address", "name": "_addr", "type": "address"}
      ],
      "name": "unbanAddress",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {"internalType": "uint256", "name": "_threadId", "type": "uint256"}
      ],
      "name": "whitelistThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    })
]

gremlinAdminABI = [json.loads(
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_gremlinThreadAddress",
          "type": "address"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [
        {"internalType": "address", "name": "_user", "type": "address"}
      ],
      "name": "banUser",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {"internalType": "uint256", "name": "_threadId", "type": "uint256"}
      ],
      "name": "blacklistThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "gremlinThread",
      "outputs": [
        {"internalType": "contract GremlinThread", "name": "", "type": "address"}
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {"internalType": "address", "name": "", "type": "address"}
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {"internalType": "address", "name": "_user", "type": "address"}
      ],
      "name": "unbanUser",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {"internalType": "uint256", "name": "_threadId", "type": "uint256"}
      ],
      "name": "whitelistThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    })
]

# Contract objects
#gremlinThreadContract = web3.eth.contract(address=gremlinThreadAddress, abi=gremlinThreadABI)
#gremlinAdminContract = web3.eth.contract(address=gremlinAdminAddress, abi=gremlinAdminABI)

# Helper Functions
def gen_poster_id():
    return '%04X' % random.randint(0, 0xffff)

def ip_to_int(ip_str):
    return int.from_bytes(
        ipaddress.ip_address(ip_str).packed,
        byteorder="little"
    ) << 8
