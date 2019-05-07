import hashlib
import os
import base64


def get_hash(plain):
    return hashlib.sha512(plain.encode('utf-8')).hexdigest()


def get_salt():
    return str(base64.b64encode(os.urandom(20)))


def validate_password(plain, salt, expected):
    return get_hash(salt + plain) == expected
