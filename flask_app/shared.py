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
import logging
import threading
import subprocess
import time

logging.basicConfig(level=logging.DEBUG)

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
gremlinThreadAddress = '0xC560Ce637fc250Ce779E2e27f8f98f4643101288'
gremlinReplyAddress = '0x5F3a28ECD4CAA8452C0d909265A714f7316E9bcd'
gremlinAdminAddress = '0x06449Af6F782661a6855fB56411712210185927f'
gremlinProfileAddress = '0x32EdCbb13De9E2d1f2346Ab94B78c2C9735eb600'
# Contract ABIs
gremlinThreadABI = [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        }
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
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        }
      ],
      "name": "ThreadDeleted",
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
        }
      ],
      "name": "ThreadWhitelisted",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "admin",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "banAddress",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "bannedAddresses",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
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
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
      ],
      "name": "deleteThread",
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
            {
              "internalType": "uint256",
              "name": "id",
              "type": "uint256"
            },
            {
              "internalType": "string",
              "name": "name",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "subject",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "email",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "magnetUrl",
              "type": "string"
            },
            {
              "internalType": "string[]",
              "name": "tags",
              "type": "string[]"
            },
            {
              "internalType": "string",
              "name": "content",
              "type": "string"
            },
            {
              "internalType": "uint256",
              "name": "parentThreadId",
              "type": "uint256"
            },
            {
              "internalType": "address",
              "name": "sender",
              "type": "address"
            },
            {
              "internalType": "uint256",
              "name": "timestamp",
              "type": "uint256"
            },
            {
              "internalType": "bool",
              "name": "whitelisted",
              "type": "bool"
            },
            {
              "internalType": "bool",
              "name": "blacklisted",
              "type": "bool"
            },
            {
              "internalType": "bool",
              "name": "deleted",
              "type": "bool"
            }
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
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
      ],
      "name": "getThread",
      "outputs": [
        {
          "components": [
            {
              "internalType": "uint256",
              "name": "id",
              "type": "uint256"
            },
            {
              "internalType": "string",
              "name": "name",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "subject",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "email",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "magnetUrl",
              "type": "string"
            },
            {
              "internalType": "string[]",
              "name": "tags",
              "type": "string[]"
            },
            {
              "internalType": "string",
              "name": "content",
              "type": "string"
            },
            {
              "internalType": "uint256",
              "name": "parentThreadId",
              "type": "uint256"
            },
            {
              "internalType": "address",
              "name": "sender",
              "type": "address"
            },
            {
              "internalType": "uint256",
              "name": "timestamp",
              "type": "uint256"
            },
            {
              "internalType": "bool",
              "name": "whitelisted",
              "type": "bool"
            },
            {
              "internalType": "bool",
              "name": "blacklisted",
              "type": "bool"
            },
            {
              "internalType": "bool",
              "name": "deleted",
              "type": "bool"
            }
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
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "threads",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "subject",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "email",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "magnetUrl",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "content",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "parentThreadId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "sender",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        },
        {
          "internalType": "bool",
          "name": "whitelisted",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "blacklisted",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "deleted",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "newAdmin",
          "type": "address"
        }
      ],
      "name": "transferAdmin",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "unbanAddress",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
      ],
      "name": "whitelistThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]

gremlinReplyABI =   [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [],
      "name": "admin",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "banAddress",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "bannedAddresses",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_replyId",
          "type": "uint256"
        }
      ],
      "name": "blacklistReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_content",
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
          "internalType": "uint256",
          "name": "_parentId",
          "type": "uint256"
        }
      ],
      "name": "createReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_replyId",
          "type": "uint256"
        }
      ],
      "name": "deleteReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getAllReplies",
      "outputs": [
        {
          "components": [
            {
              "internalType": "uint256",
              "name": "id",
              "type": "uint256"
            },
            {
              "internalType": "string",
              "name": "content",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "email",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "magnetUrl",
              "type": "string"
            },
            {
              "internalType": "uint256",
              "name": "parentId",
              "type": "uint256"
            },
            {
              "internalType": "address",
              "name": "sender",
              "type": "address"
            },
            {
              "internalType": "uint256",
              "name": "timestamp",
              "type": "uint256"
            },
            {
              "internalType": "bool",
              "name": "whitelisted",
              "type": "bool"
            },
            {
              "internalType": "bool",
              "name": "blacklisted",
              "type": "bool"
            }
          ],
          "internalType": "struct GremlinReply.Reply[]",
          "name": "",
          "type": "tuple[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "replies",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "internalType": "string",
          "name": "content",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "email",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "magnetUrl",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "parentId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "sender",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        },
        {
          "internalType": "bool",
          "name": "whitelisted",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "blacklisted",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "replyCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "unbanAddress",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_replyId",
          "type": "uint256"
        }
      ],
      "name": "whitelistReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]

gremlinAdminABI = [
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_gremlinThreadAddress",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_gremlinReplyAddress",
          "type": "address"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_user",
          "type": "address"
        }
      ],
      "name": "banUser",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_replyId",
          "type": "uint256"
        }
      ],
      "name": "blacklistReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
      ],
      "name": "blacklistThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_replyId",
          "type": "uint256"
        }
      ],
      "name": "deleteReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
      ],
      "name": "deleteThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "gremlinReply",
      "outputs": [
        {
          "internalType": "contract GremlinReply",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "gremlinThread",
      "outputs": [
        {
          "internalType": "contract GremlinThread",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_user",
          "type": "address"
        }
      ],
      "name": "unbanUser",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_replyId",
          "type": "uint256"
        }
      ],
      "name": "whitelistReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
      ],
      "name": "whitelistThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]

gremlinProfileABI = [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "user",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "name",
          "type": "string"
        }
      ],
      "name": "ProfileCreated",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "user",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "field",
          "type": "string"
        }
      ],
      "name": "ProfileUpdated",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "user",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "videoStreamUrl",
          "type": "string"
        }
      ],
      "name": "StreamUrlUpdated",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "bio",
          "type": "string"
        }
      ],
      "name": "createProfile",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "user",
          "type": "address"
        }
      ],
      "name": "getProfile",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "user",
          "type": "address"
        }
      ],
      "name": "getStreamUrl",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "profiles",
      "outputs": [
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "bio",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "css",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "html",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "videoStreamUrl",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "css",
          "type": "string"
        }
      ],
      "name": "updateProfileCSS",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "html",
          "type": "string"
        }
      ],
      "name": "updateProfileHTML",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "videoStreamUrl",
          "type": "string"
        }
      ],
      "name": "updateStreamUrl",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]



FILE_DIR = 'static'
TORRENT_DIR = 'torrents'
TRACKER_PORT = 80
SEED_FILE = 'seeded_files.json'
BLACKLIST_FILE = 'blacklist.json'
WHITELIST_FILE = 'whitelist.json'
TRACKER_URLS = [
    "wss://tracker.openwebtorrent.com",
    #"wss://tracker.btorrent.xyz",
    #"wss://tracker.fastcast.nz",
    #"wss://tracker.webtorrent.io"
]

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

seeded_files = {}
THREADS = []

def load_blacklist():
    if not os.path.exists(BLACKLIST_FILE):
        return []  # Return empty list if file does not exist
    with open(BLACKLIST_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []  # Return empty list if file is corrupt or empty

# Load whitelist from file, if it exists, otherwise return an empty list
def load_whitelist():
    if not os.path.exists(WHITELIST_FILE):
        return []  # Return empty list if file does not exist
    with open(WHITELIST_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []  # Retur



blacklist = load_blacklist()
whitelist = load_whitelist()


def save_blacklist(data):
    with open(BLACKLIST_FILE, 'w') as f:
        json.dump(data, f)


def save_whitelist(data):
    with open(WHITELIST_FILE, 'w') as f:
        json.dump(data, f)


# Helper Functions
def gen_poster_id():
    return '%04X' % random.randint(0, 0xffff)

def ip_to_int(ip_str):
    return int.from_bytes(
        ipaddress.ip_address(ip_str).packed,
        byteorder="little"
    ) << 8

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def seed_file(file_path):
    """Function to seed the file using the WebTorrent command and return the magnet URL without waiting for the process to exit."""
    try:
        # Check if the file is already being seeded
        if file_path in seeded_files:
            logging.info(f"{file_path} is already being seeded.")
            return seeded_files[file_path]  # Return existing magnet URL if it's already seeded

        # Prepare tracker list for WebTorrent seed command
        tracker_list = " ".join([f"--announce={tracker}" for tracker in TRACKER_URLS])

        # WebTorrent seed command with trackers and keep-seeding
        cmd = f"webtorrent seed '{file_path}' {tracker_list} --keep-seeding"
        logging.info(f"Running seeding command: {cmd}")

        # Run the command in a subprocess
        process = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )

        magnet_url = None

        # Function to monitor the output of the WebTorrent process
        def monitor_output():
            nonlocal magnet_url
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break

                if output:
                    #logging.info(f"WebTorrent output: {output.strip()}")
                    if "Magnet:" in output:
                        magnet_url = output.split("Magnet: ")[1].strip()
                        seeded_files[file_path] = magnet_url
                        logging.info(f"Magnet URL found: {magnet_url}")
                        break  # Magnet URL found, exit the loop

        # Start monitoring output in a separate thread
        output_thread = threading.Thread(target=monitor_output)
        output_thread.start()

        # Wait for the magnet URL to be extracted
        output_thread.join(timeout=30)  # Wait for up to 10 seconds for the magnet URL to appear

        if magnet_url:
            logging.info(f"Magnet URL returned: {magnet_url}")
            return magnet_url
        else:
            logging.error(f"Failed to retrieve the magnet URL in time.")
            return None

    except Exception as e:
        logging.error(f"Error while seeding file: {str(e)}")
        return None

class StreamSeed(threading.Thread):
    """Threaded class for seeding HLS segments using WebTorrent."""
    
    def __init__(self, eth_addr, filename):
        super().__init__()
        self.eth_addr = eth_addr
        self.filename = filename
        self.magnet_url = None
        self.file_exists = False
        self.daemon = True  # Make the thread run as a daemon
        
    def check_file_exists(self):
        """Check if the file exists before proceeding."""
        while not os.path.exists(self.filename):
            logging.info(f"Waiting for file {self.filename} to appear...")
            time.sleep(1)  # Wait for the file to be written
        self.file_exists = True
        logging.info(f"File {self.filename} found, starting seeding process...")

    def seed_file(self):
        """Function to seed the file using the WebTorrent command and return the magnet URL."""
        if self.eth_addr not in seeded_files:
            seeded_files[self.eth_addr] = set()

        # Check if the file has already been seeded
        if self.filename in seeded_files[self.eth_addr]:
            logging.info(f"{self.filename} is already being seeded for {self.eth_addr}.")
            return

        # Prepare the WebTorrent seed command
        cmd = f"webtorrent seed {self.filename} --keep-seeding"
        logging.info(f"Running seeding command: {cmd}")
        
        # Run the WebTorrent command
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        def monitor_output():
            """Monitor the WebTorrent output to find the magnet URL."""
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    logging.info(f"WebTorrent output: {output.strip()}")
                    if "Magnet:" in output:
                        self.magnet_url = output.split("Magnet: ")[1].strip()
                        seeded_files[self.eth_addr].add(self.magnet_url)
                        logging.info(f"Magnet URL for {self.eth_addr}: {self.magnet_url}")
                        break
        
        monitor_output()

    def run(self):
        """Main method that runs in the thread."""
        self.check_file_exists()
        if self.file_exists:
            self.seed_file()


def auto_seed_static_files():
    """Automatically seed all allowed files in the static directory."""
    for filename in os.listdir(FILE_DIR):
        file_path = os.path.join(FILE_DIR, filename)
        if os.path.isfile(file_path) and allowed_file(filename):
            #logging.info(f"Automatically seeding {file_path}")
            seed_thread = threading.Thread(target=seed_file, args=(file_path,))
            seed_thread.start()
