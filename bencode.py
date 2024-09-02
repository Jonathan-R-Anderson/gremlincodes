# bencode.py -- deals with bencoding

""" This module deals with the encoding and decoding of bencoded data.
decode() and encode() are the major functions available, to decode
and encode data. """

# Note: Bencoding specification:
# http://www.bittorrent.org/beps/bep_0003.html

def encode_int(data):
    """ Given an integer, returns a bencoded string of that integer. """
    if not isinstance(data, int):
        raise TypeError(f"Expected int, got {type(data)}")
    return b"i" + str(data).encode() + b"e"

def encode_str(data):
    """ Given a string, returns a bencoded string of that string. """
    if not isinstance(data, str):
        raise TypeError(f"Expected str, got {type(data)}")
    return str(len(data)).encode() + b":" + data.encode()

def encode_bytes(data):
    """ Given a bytes object, return a bencoded string. """
    if not isinstance(data, bytes):
        raise TypeError(f"Expected bytes, got {type(data)}")
    return str(len(data)).encode() + b":" + data

def encode_list(data):
    """ Given a list, returns a bencoded list. """
    if not isinstance(data, list):
        raise TypeError(f"Expected list, got {type(data)}")
    return b"l" + b"".join([encode(item) for item in data]) + b"e"

def encode_dict(data):
    """ Given a dictionary, return the bencoded dictionary. """
    if not isinstance(data, dict):
        raise TypeError(f"Expected dict, got {type(data)}")
    temp = []
    for key in sorted(data.keys()):
        if isinstance(key, str):
            encoded_key = encode_str(key)
        elif isinstance(key, bytes):
            encoded_key = encode_bytes(key)
        else:
            raise TypeError(f"Unsupported key type: {type(key)}")
        temp.append(encoded_key + encode(data[key]))
    return b"d" + b"".join(temp) + b"e"

# Update the encode_functions dictionary
encode_functions = {
    int: encode_int,
    str: encode_str,
    list: encode_list,
    dict: encode_dict,
    bytes: encode_bytes
}

def encode(data):
    """ Dispatches data to appropriate encode function. """
    try:
        return encode_functions[type(data)](data)
    except KeyError:
        raise TypeError(f"Unsupported data type: {type(data)}")

def decode_int(data):
    """ Given a bencoded string of an integer, returns the integer. """
    if not data.startswith(b"i") or not data.endswith(b"e"):
        raise ValueError("Invalid bencoded integer")
    return int(data[1:-1])

def decode_str(data):
    """ Given a bencoded string, returns the decoded string. """
    colon_pos = data.find(b":")
    if colon_pos == -1:
        raise ValueError("Invalid bencoded string")
    length = int(data[:colon_pos])
    return data[colon_pos + 1:colon_pos + 1 + length]

def decode_bytes(data):
    """ Given a bencoded string, returns the decoded bytes. """
    return decode_str(data)

def decode_list(data):
    """ Given a bencoded list, return the unencoded list. """
    if not data.startswith(b"l") or not data.endswith(b"e"):
        raise ValueError("Invalid bencoded list")
    return [decode(item) for item in inflate(data[1:-1])]

def decode_dict(data):
    """ Given a bencoded dictionary, return the dictionary. """
    if not data.startswith(b"d") or not data.endswith(b"e"):
        raise ValueError("Invalid bencoded dictionary")
    items = inflate(data[1:-1])
    temp = {}
    for i in range(0, len(items), 2):
        key = decode(items[i])
        value = decode(items[i + 1])
        temp[key] = value
    return temp

# Update the decode_functions dictionary
decode_functions = {
    b"i": decode_int,
    b"l": decode_list,
    b"d": decode_dict,
}

def decode(data):
    """ Dispatches data to appropriate decode function. """
    if data.startswith(b"i"):
        return decode_int(data)
    elif data.startswith(b"l"):
        return decode_list(data)
    elif data.startswith(b"d"):
        return decode_dict(data)
    elif b":" in data:
        return decode_str(data)
    else:
        raise TypeError("Invalid bencoded data")
