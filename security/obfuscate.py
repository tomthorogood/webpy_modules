#!/usr/bin/env python

def hash_this (string):
    """
    Returns a hash value. Should probably allow users to set the number of times they'd lke something hashed.
    """
    import hashlib
    return hashlib.sha224(string).hexdigest()
