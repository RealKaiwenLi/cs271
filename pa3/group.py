from crypto import *
import rsa

index = 0

def create_new_group(client):
    global index
    group_id = client + str(index)
    index += 1
    publicKey, privateKey = rsa.newkeys(128)
    publicKeyPem = publicKey.save_pkcs1()
    privateKeyPem = privateKey.save_pkcs1()
    return group_id, publicKeyPem, privateKeyPem

group_id, serial_pub, serial_private = create_new_group("A")


def read_message(client, group):
    group = {'members': [], 'group_id': group, 'messages': []}
    with open(f'{client}.txt', 'rb') as f:
        log = f.read()
        index = 0
        while index < len(log):
            idx = log[index:index+1].decode()
            event = log[index+1:index+2].decode()
            group_id = log[index+2:index+4].decode()
            #create event
            if event == '0' and group_id == group['group_id']:
                mem_number = log[index+4:index+5].decode()
                index += 5
                key_set = {}
                for i in range(0,int(mem_number)):
                    key_set[log[5+i:5+i+1].decode()] = log[5+int(mem_number) + i*256:5+int(mem_number) + i*256 + 256]
                    index += 257
                group['members'] = [char for char in key_set.keys()]
            #add event
            if event == '1' and group_id == group:
                pass
            #kick event
            if event == '2' and group_id == group:
                pass
            #write event
            # if event == '3' and group_id == group and client in group['members']:
            #     pass

        return group            

print(read_message("A",'A0'))
# public_key, private_key = rsa.newkeys(2048)

# res = encrypt_message(serial_private, public_key)
# a = [b'1',b'0',b'A0', b'2', b'AB', res, res]
# log = b''.join(a)
# with open('A.txt', 'ab') as f:
#     f.write(log)
# index = log[0:1].decode()
# event = log[1:2].decode()
# group_id = log[2:4].decode()
# mem_number = log[4:5].decode()
# key_set = {}
# for i in range(0,int(mem_number)):
#     key_set[log[5+i:5+i+1].decode()] = log[5+int(mem_number) + i*256:5+int(mem_number) + i*256 + 256]
# print(index, event, group_id, mem_number, key_set)
# # print(log[0:1].decode())
# # print(log[1:2].decode())
# # print(res)
# # print(a[2:][0])

# key = decrypt_message(key_set['A'], private_key)

# s = b'hello'
# pub_key = rsa.PublicKey.load_pkcs1(serial_pub)
# pri_key = rsa.PrivateKey.load_pkcs1(key)

# encryp = encrypt_message(s, pub_key)
# resp = decrypt_message(encryp, pri_key)
# # print(resp)
