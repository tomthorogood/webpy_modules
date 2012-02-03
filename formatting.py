#!/usr/bin/env python

def append_with_commas (prefix="", values=[], suffix="", quote=True):
    """
    strings a list of entries together, adding a comma after all except the last one.
    A prefix and suffix can be defined to return a complete string.
    prefix = "Hello, I like: " 
    values = ["Apples", "Pears", "Bananas", "Ghost meat"]
    suffix = " but not on Wednesday afternoons."
    quote=False

    will return:
        "Hello, I like Apples, Pears, Bananas, Ghost meat but not on Wednesday afternoons."


    """
    ret_str = prefix                #ret_str = "returned string"
    commas = len(values)-1          #number of commas allowed
    c = 0                           #number of commas inserted
    for value in values:
        if not quote:
            ret_str += "%s" % value
        elif quote:
            ret_str += "\"%s\"" % value
        if c < commas:
            ret_str += ", "
        c+= 1
    ret_str += suffix
    return ret_str

def convert_to_tinyint (val):
    """
    Checks a value against the true/false table below and converts to 1/0 for use in a TINYINT column.
    If the value does not match an entry in either truths or falses, an exception is forced in order
    to keep the list growing from a development perspective.
    """
    truths = (
            '1', 'true', 'yes', 'can', 'do', 'contact', 'public'
            )
    falses = (
            '0', 'false', 'no', 'cannot', 'can\'t', 'do not', 'don\'t', 'do not contact', 'private'
            )
    if val.lower() in truths:
        return 1
    elif val.lower() in falses:
        return 0
    else:
        raise KeyError
