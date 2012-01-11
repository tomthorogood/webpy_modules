#!/usr/bin/env python

def append_with(char=",",prefix="", values=[], suffix="", quote=True):
    ret_str = prefix                #ret_str = "returned string"
    commas = len(values)-1          #number of commas allowed
    c = 0                           #number of commas inserted
    for value in values:
        if not quote:
            ret_str += "%s" % value
        elif quote:
            ret_str += "\"%s\"" % value
        if c < commas:
            ret_str += "%s " % char
        c+= 1
    ret_str += suffix
    return ret_str


def append_with_commas (prefix="", values=[], suffix="", quote=True):
    return append_with(',' , prefix, values, suffix, quote)


def convert_to_list (dictionary={}, join='=',quote=False):
    """Converts a dictionary into a list."""
    l = []
    for key in dictionary:
        entry = "%s%s"%(str(key), join)
        if quote=='single':
            entry += "\'%s\'" % dictionary[key]
        elif quote=='double':
            entry += "\"%s\"" % dictionary[key]
        else:
            entry += str(dictionary[key])
        l.append(entry)

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
