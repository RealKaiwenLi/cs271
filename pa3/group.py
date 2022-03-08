from crypto import *
import rsa


index = 0

def create_new_group(client):
    global index
    group_id = client + str(index)
    index += 1
    publicKey, privateKey = rsa.newkeys(256)
    publicKeyPem = publicKey.save_pkcs1()
    privateKeyPem = privateKey.save_pkcs1()
    return group_id, publicKeyPem, privateKeyPem

group_id, serial_pub, serial_private = create_new_group("A")

private_list = [serial_private[i:i+16] for i in range(0, len(serial_private), 16)]

public_key, private_key = rsa.newkeys(256)
list = []
for i in private_list:
    list.append(encrypt_message(i, public_key))

ans = []
for i in list:
    ans.append(decrypt_message(i, private_key))

print(list)
key = b''.join(ans)

s = b'hello'
pub_key = rsa.PublicKey.load_pkcs1(serial_pub)
pri_key = rsa.PrivateKey.load_pkcs1(serial_private)

encryp = encrypt_message(s, pub_key)
res = decrypt_message(encryp, pri_key)
print(res)
