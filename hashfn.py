import hashlib


def getHash(strValue):

    input_bytes = strValue.encode('utf-8')

    # Create a new SHA-256 hash object
    hash_object = hashlib.sha256(input_bytes)

    # Get the hash value in hexadecimal format
    return hash_object.hexdigest()
