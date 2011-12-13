#!/usr/bin/env python

def append_with_commas (prefix="", values=[], suffix="", quote=True):
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
