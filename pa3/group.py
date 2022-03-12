from crypto import *
import rsa
from read_log import *
from crypto import *

index = 0

def create_new_group(client):
    global index
    group_id = client + str(index)
    index += 1
    publicKey, privateKey = rsa.newkeys(128)
    publicKeyPem = publicKey.save_pkcs1()
    privateKeyPem = privateKey.save_pkcs1()
    return group_id, publicKeyPem, privateKeyPem

def encrypt_group_key(client, term, members, event, group_id=None):
    groups, serial_pub, serial_private = create_new_group(client)
    print(f'create group {groups} with {members}')
    keys = get_all_public_keys()
    pk_encrypted = []
    for member in members:
        mes = encrypt_message(serial_private, keys[member])
        pk_encrypted.append(mes)
    if group_id == None:
        group_id = groups
    tmp = [str(term).encode(),event.encode(),group_id.encode(), serial_pub, str(len(members)).encode(), members.encode()]
    final_byte = tmp + pk_encrypted
    log = b''.join(final_byte)
    return log

def read_message(client, group_num):
    log = ''
    with open(f'A.txt', 'rb') as f:
        log = f.read()
    group = {'members': {}, 'group_id': group_num, 'messages': [], 'pub_key': ''}
    index = 0
    while index < len(log):
        idx = log[index:index+1].decode()
        event = log[index+1:index+2].decode()
        group_id = log[index+2:index+4].decode()
        # print(idx, event, group_id)
        # #create event
        if event == '0' and group_id == group['group_id']:
            # print('create event')
            serial_pub_key = log[index+4:index+4+97]
            mem_number = log[index+101:index+102].decode()
            index += 102
            key_set = {}
            mem_index = index
            index += int(mem_number)
            for i in range(0,int(mem_number)):
                key_set[log[mem_index:mem_index+1].decode()] = log[index: index+256]
                mem_index += 1
                index += 256
            group['members'] = key_set
            group['pub_key'] = serial_pub_key
        # #add event
        if event == '1' and group_id == group['group_id']:
            # print('add new member')
            member = log[index+4:index+5].decode()
            a_mem = list(group['members'].items())[0]
            group_private_key = decrypt_message(a_mem[1], get_private_key(a_mem[0]))
            keys = get_all_public_keys()
            encrypt_key = encrypt_message(group_private_key, keys[member])

            group['members'][member] = encrypt_key

            index += 257+4
        # #kick event
        if event == '2' and group_id == group['group_id']:
            # print('kick member')
            serial_pub_key = log[index+4:index+4+97]
            mem_number = log[index+101:index+102].decode()
            index += 102
            key_set = {}
            mem_index = index
            index += int(mem_number)
            for i in range(0,int(mem_number)):
                key_set[log[mem_index:mem_index+1].decode()] = log[index: index+256]
                mem_index += 1
                index += 256
            group['members'] = key_set
            group['pub_key'] = serial_pub_key
        # write event
        if event == '3' and group_id == group['group_id']:
            # print('write message')
            if client in group['members'].keys():
                member = log[index+4:index+5].decode()
                mes = log[index+5:index+5+16]
                if member in group['members'].keys():
                    group_private_key = get_group_private_key(decrypt_message(group['members'][client], get_private_key(client)))
                    message = decrypt_message(mes, group_private_key).decode()
                    group['messages'].append(message)
            index += 21
    return group

def add_member(client, term, group_num, member):
    group = read_message(client, group_num)
    if member in group['members'].keys() or client not in group['members'].keys():
        return 'Error: member already in group or you are not in this group'
    else:
        keys = get_all_public_keys()
        group_private_key = decrypt_message(group['members'][client], get_private_key(client))
        envrypted_key = encrypt_message(group_private_key, keys[member])
        tmp = [str(term).encode(),b'1',group_num.encode(), member.encode(), envrypted_key]
        log = b''.join(tmp)
        return log

def kick_member(client, term, group_num, member):
    members = read_message(client, group_num)['members']
    if client not in members.keys() or member not in members.keys():
        return "Error: You are not in this group or member is not in this group"
    members.pop(member)
    member = ''.join(members)
    log = encrypt_group_key(client, term, member, '2', group_num)
    return log

def write_message(client, term, group_num, message):
    group = read_message(client, group_num)
    encrypt_mes = encrypt_message(message.encode(), rsa.PublicKey.load_pkcs1(group['pub_key']))
    tmp = [str(term).encode(),b'3',group_num.encode(), client.encode(), encrypt_mes]
    log = b''.join(tmp)
    return log

# with open('A.txt', 'wb') as f:
#     pass
# log = encrypt_group_key("A","ABC", '0')
# with open('A.txt', 'ab') as f:
#     f.write(log)
# log = add_member("A", "A0", "D")
# with open('A.txt', 'ab') as f:
#     f.write(log)
# log = write_message('A','A0','gg')
# with open('A.txt', 'ab') as f:
#     f.write(log)
# log = kick_member('A','A0','C')
# with open('A.txt', 'ab') as f:
#     f.write(log)
# log = write_message('A','A0','Hlo')
# with open('A.txt', 'ab') as f:
#     f.write(log)
# log = write_message('A','A0','Hlo1')
# with open('A.txt', 'ab') as f:
#     f.write(log)
# log = write_message('E','A0','Hlo2')
# with open('A.txt', 'ab') as f:
#     f.write(log)
# res = read_message("D","A0")
# print(res['messages'])










