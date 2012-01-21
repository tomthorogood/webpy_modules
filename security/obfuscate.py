#!/usr/bin/env python

def hash_this (string):
    import hashlib
    return hashlib.sha224(string).hexdigest()
