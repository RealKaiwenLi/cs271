import rsa

def read_public(filename):
    with open(filename, "rb") as key_file:
        public_key = rsa.PublicKey.load_pkcs1(key_file.read())
    return public_key

def get_all_public_keys():
    keys = {"A": "A_public.pem", "B": "B_public.pem", "C": "C_public.pem", "D": "D_public.pem", "E": "E_public.pem"}
    for key in keys.keys():
        keys[key] = read_public(keys[key])

    return keys

def get_private_key(clientName):
    with open(f"{clientName}_private.pem", "rb") as key_file:
        private_key = rsa.PrivateKey.load_pkcs1(key_file.read())
    return private_key


def encrypt_message(message, public_key):
    encMessage = rsa.encrypt(message, public_key)
    return encMessage

def decrypt_message(message, private_key):
    decMessage = rsa.decrypt(message, private_key)
    return decMessage


def get_group_private_key(key):
    private_key = rsa.PrivateKey.load_pkcs1(key)
    return private_key