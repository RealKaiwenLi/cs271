import rsa
import json

from jinja2 import MemcachedBytecodeCache


# public_key, private_key = rsa.newkeys(2048)

# # private key
# serial_private = private_key.save_pkcs1()
# with open('D_private.pem', 'wb') as f: f.write(serial_private)
    
# # public key
# serial_pub = public_key.save_pkcs1()
# with open('D_public.pem', 'wb') as f: f.write(serial_pub)

#########      Private device only    ##########
def read_private (filename = "A_private.pem"):
    with open(filename, "rb") as key_file:
        private_key = rsa.PrivateKey.load_pkcs1(key_file.read())
    return private_key
                  
######### Public (shared) device only ##########
def read_public (filename = "A_public.pem"):
    with open(filename, "rb") as key_file:
        public_key = rsa.PublicKey.load_pkcs1(key_file.read())
    return public_key

data = [b'My secret weight', b'My secret id']
public_key = read_public()


private_key = read_private()




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
