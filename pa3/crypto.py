import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def read_public (filename = "A_public.pem"):
    with open("A_public.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key

def get_all_public_keys():
    keys = {"A": "A_public.pem", "B": "B_public.pem", "C": "C_public.pem", "D": "D_public.pem", "E": "E_public.pem"}
    for key in keys.keys():
        keys[key] = read_public(keys[key])

    return keys

def get_private_key(clientName):
    with open(f"{clientName}_private.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key

get_private_key("A")
