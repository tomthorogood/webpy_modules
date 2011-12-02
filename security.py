def hash_this (string):
    import hashlib
    hashed_string = hashlib.sha224(string).hexdigest()
    return hashed_string
