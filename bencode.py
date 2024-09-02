# bencode.py -- deals with bencoding
# Written by Joe Salisbury <salisbury.joseph@gmail.com>
#
# You are free to use this code in any way you see fit, on the basis
# that if it is used, modified, or distributed, proper accreditation
# of the original author remains.

""" This module deals with the encoding and decoding of bencoded data.
decode() and encode() are the major functions available, to decode
and encode data. """

import types
from util import collapse

def stringlength(string, index=0):
    """ Given a bencoded expression, starting with a string, returns
    the length of the string. """
    try:
        colon = string.find(":", index)  # Find the colon, ending the number.
    except ValueError:
        raise BencodeError("Decode", "Malformed expression", string)

    # Return a list of the number characters.
    num = [a for a in string[index:colon] if a.isdigit()]
    n = int(collapse(num))  # Collapse them, and turn them into an int.

    # Return the length of the number, colon, and the string length.
    return len(num) + 1 + n

def walk(exp, index=1):
    """ Given a compound bencoded expression, as a string, returns
    the index of the end of the first dict, or list.
    Start at an index of 1, to avoid the start of the actual list. """
    if exp[index] == "i":
        endchar = exp.find("e", index)
        return walk(exp, endchar + 1)
    elif exp[index].isdigit():
        strlength = stringlength(exp, index)
        return walk(exp, index + strlength)
    elif exp[index] in ["l", "d"]:
        endsub = walk(exp[index:], 1)
        return walk(exp, index + endsub)
    elif exp[index] == "e":
        index += 1
        return index

def inflate(exp):
    """ Given a compound bencoded expression, as a string, returns the
    individual data types within the string as items in a list.
    Note, that lists and dicts will come out not inflated. """
    if exp == "":
        return []
    if ben_type(exp) == int:
        end = exp.find("e")
        x = exp[:end + 1]
        xs = inflate(exp[end + 1:])
    elif ben_type(exp) == str:
        strlength = stringlength(exp)
        x = exp[:strlength]
        xs = inflate(exp[strlength:])
    elif ben_type(exp) in [list, dict]:
        end = walk(exp)
        x = exp[:end]
        xs = inflate(exp[end:])
    return [x] + xs

def ben_type(exp):
    """ Given a bencoded expression, returns what type it is. """
    if exp[0] == "i":
        return int
    elif exp[0].isdigit():
        return str
    elif exp[0] == "l":
        return list
    elif exp[0] == "d":
        return dict

def check_type(exp, datatype):
    """ Given an expression, and a datatype, checks the two against
    each other. """
    if not isinstance(exp, datatype):
        raise BencodeError("Encode", "Malformed expression", exp)

def check_ben_type(exp, datatype):
    """ Given a bencoded expression, and a datatype, checks the two
    against each other. """
    if ben_type(exp) != datatype:
        raise BencodeError("Decode", "Malformed expression", exp)

class BencodeError(Exception):
    """ Raised if an error occurs encoding or decoding. """

    def __init__(self, mode, value, data):
        assert mode in ["Encode", "Decode"]
        self.mode = mode
        self.value = value
        self.data = data

    def __str__(self):
        return repr(f"{self.mode}: {self.value} : {str(self.data)}")

def encode_int(data):
    check_type(data, int)
    return f"i{data}e"

def decode_int(data):
    check_ben_type(data, int)
    try:
        end = data.index("e")
    except ValueError:
        raise BencodeError("Decode", "Cannot find end of integer expression", data)

    t = data[1:end]
    if len(t) > 1 and t[0] == "0":
        raise BencodeError("Decode", "Malformed expression, leading zeros", data)

    return int(t)

def encode_str(data):
    check_type(data, str)
    return f"{len(data)}:{data}"

def encode_bytes(data):
    check_type(data, bytes)
    return str(len(data)).encode() + b":" + data

def decode_str(data):
    check_ben_type(data, str)
    try:
        colon = data.find(":")
    except ValueError:
        raise BencodeError("Decode", "Badly formed expression", data)

    strlength = stringlength(data)
    return data[colon + 1:strlength]

def encode_list(data):
    check_type(data, list)
    if data == []:
        return "le"
    temp = [encode(item) for item in data]
    return "l" + collapse(temp) + "e"

def decode_list(data):
    check_ben_type(data, list)
    if data == "le":
        return []
    temp = inflate(data[1:-1])
    return [decode(item) for item in temp]

def encode_dict(data):
    check_type(data, dict)
    if data == {}:
        return "de"
    temp = [encode_str(key) + encode(data[key]) for key in sorted(data.keys())]
    return "d" + collapse(temp) + "e"

def decode_dict(data):
    check_ben_type(data, dict)
    if data == "de":
        return {}
    data = data[1:-1]
    temp = {}
    terms = inflate(data)
    count = 0
    while count != len(terms):
        temp[decode_str(terms[count])] = decode(terms[count + 1])
        count += 2
    return temp

# Dictionaries of the data type, and the function to use
encode_functions = {
    int: encode_int,
    str: encode_str,
    list: encode_list,
    dict: encode_dict,
    bytes: encode_bytes  # Add the new handler for bytes
}

decode_functions = {
    int: decode_int,
    str: decode_str,
    list: decode_list,
    dict: decode_dict
}

def encode(data):
    try:
        return encode_functions[type(data)](data)
    except KeyError:
        raise BencodeError("Encode", "Unknown data type", data)

def decode(data):
    try:
        return decode_functions[ben_type(data)](data)
    except KeyError:
        raise BencodeError("Decode", "Unknown data type", data)
