import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import json


# private_key = rsa.generate_private_key(
#     public_exponent=65537,
#     key_size=2048,
#     backend=default_backend()
# )
# public_key = private_key.public_key()

# # private key
# serial_private = private_key.private_bytes(
#     encoding=serialization.Encoding.PEM,
#     format=serialization.PrivateFormat.PKCS8,
#     encryption_algorithm=serialization.NoEncryption()
# )
# with open('E_private.pem', 'wb') as f: f.write(serial_private)
    
# # public key
# serial_pub = public_key.public_bytes(
#     encoding=serialization.Encoding.PEM,
#     format=serialization.PublicFormat.SubjectPublicKeyInfo
# )
# with open('E_public.pem', 'wb') as f: f.write(serial_pub)

#########      Private device only    ##########
def read_private (filename = "B_private.pem"):
    with open(filename, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key
                  
######### Public (shared) device only ##########
def read_public (filename = "B_public.pem"):
    with open(filename, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key

str = b'My secret weight'
public_key = read_public()
encrypted = public_key.encrypt(
        str,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
private_key = read_private()
res = (
            private_key.decrypt(
                encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )))

print(res)


def reset():
    c = ['A', 'B', 'C', 'D', 'E']
    for i in c:
        state = open(f'{i}_state.txt')
        states = state.readlines()
        state.close()

        new_state = json.loads(states[0])
        new_state['currentTerm'] = 0
        new_state['votedFor'] = None
        states[0] = json.dumps(new_state)+'\n'
        state = open(f'{i}_state.txt','w')
        new_file_contents = "".join(states)
        state.write(new_file_contents)
        state.close()

reset()