from _thread import *
import time
import socket
import sys
from time import sleep
import PySimpleGUI as sg
import json
from datetime import datetime
from crypto import *
from group import *
from read_log import *
import random

class myClient:
    def __init__(self, clientName) -> None:
        self.name = clientName
        self.clinetIPs = '127.0.0.1'
        self.role = 'follower'
        self.currentTerm = 0
        self.currLeader = None
        self.votedFor = None
        self.log = open(clientName + '.txt', 'a')
        self.state = self.name + '_state.txt'
        self.public_keys = get_all_public_keys()
        self.fail_clients = []
        with open(self.state, 'r') as f:
            try:
                last_line = f.readlines()[0]
            except:
                last_line = '0 0'
            
            last_line = json.loads(last_line)
            self.currentTerm = last_line['currentTerm']
            self.votedFor = last_line['votedFor']
        self.votes_received = 0
        self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ServerSocket.settimeout(random.uniform(5,10))
        self.clientPorts = {'A': 1111, 'B': 2222, 'C': 3333, 'D': 4444, 'E': 5555}
        try:
            self.ServerSocket.bind((self.clinetIPs, self.clientPorts[self.name]))
        except socket.error as e:
            print(str(e))
        start_new_thread(self.send_heartbeat, ())
        start_new_thread(self.listen_to_all,())
        self.startGUI()

    def update_current_term(self, term):
        self.currentTerm = term
        state = open(f'{self.name}_state.txt')
        states = state.readlines()
        state.close()

        new_state = json.loads(states[0])
        new_state['currentTerm'] = term
        states[0] = json.dumps(new_state)+'\n'
        state = open(f'{self.name}_state.txt','w')
        new_file_contents = "".join(states)
        state.write(new_file_contents)
        state.close()

    def update_voted_for(self, client):
        self.votedFor = client
        state = open(f'{self.name}_state.txt')
        states = state.readlines()
        state.close()

        new_state = json.loads(states[0])
        new_state['votedFor'] = client
        states[0] = json.dumps(new_state)+'\n'
        state = open(f'{self.name}_state.txt','w')
        new_file_contents = "".join(states)
        state.write(new_file_contents)
        state.close()

    #send heartbeat to all followers if I'm a leader
    def send_heartbeat(self):
        while True:
            if self.role == 'leader':
                self.broadcast_to_all(f'heartbeat {self.name} {self.currentTerm}')

    def append_to_log(self, msg):
        with open(self.name + '.txt', 'a') as f:
            f.write(msg)
            f.write('\n')

    #start election
    def start_election(self):
        self.update_current_term(self.currentTerm + 1)
        self.role = 'candidate'
        print("Set as candidate for term: ", self.currentTerm)
        last_log = get_last_log(self.name)
        self.votes_received = 1
        self.update_voted_for(self.name)
        msg = f'RequestVote {self.name} {self.currentTerm} {last_log}'
        self.broadcast_to_all(msg)
    
    def complete_log(self, index, term):
        log = get_last_log(self.name).split(' ')
        return (term > int(log[1])) or (term == int(log[1]) and index >= int(log[0]))
    
    
    def process_request_vote(self, msg):
        msg_list = msg.split(' ')
        term = int(msg_list[2])
        log_ok = self.votedFor == None or self.complete_log(int(msg_list[3]), int(msg_list[4]))
        term_ok = term > self.currentTerm or (term == self.currentTerm and (self.votedFor == None or self.votedFor == msg_list[1]))
        if log_ok and term_ok:
            self.update_current_term(term)
            self.role = 'follower'
            self.update_voted_for(msg_list[1])
            self.send_direct_msg(f'Vote {self.name} {self.currentTerm}', msg_list[1])

    def broadcast_to_all(self, msg):
        for item in self.clientPorts:
            if item != self.name and item not in self.fail_clients:
                self.ServerSocket.sendto(str.encode(msg), (self.clinetIPs, self.clientPorts[item]))
                sleep(0.5)
        
    def send_direct_msg(self, msg, receiver):
        if receiver not in self.fail_clients:
            self.ServerSocket.sendto(str.encode(msg), (self.clinetIPs, self.clientPorts[receiver]))
                
    def listen_to_all(self):
        print(f'client {self.name} is listening now')
        while True:
            try:
                data, addr = self.ServerSocket.recvfrom(4096*10)
                client = self.get_client(addr[1])
                #use first byte to identify
                # print(data[0:1])
                if client not in self.fail_clients:
                    if (data[0:1] == b'h'):
                        self.role = 'follower'
                        self.currLeader = client
                        self.currentTerm = max(int(data.decode('utf-8').split(' ')[2]), self.currentTerm)

                    if (data[0:1] == b'R'):
                        print(data.decode('utf-8'))
                        self.process_request_vote(data.decode('utf-8'))

                    if (data[0:1] == b'V'):
                        self.votes_received += 1
                        if self.votes_received > len(self.clientPorts) / 2 and self.role == 'candidate':
                            self.role = 'leader'
                            self.currLeader = self.name
                            print(f'I am the leader now')
                            self.ServerSocket.settimeout(None)
                    
                    if (data.decode('utf-8').split(' ')[0] == 'redirect'):
                        #TODO: rewrite decode part
                        msg = data.decode('utf-8')[9:]
                        self.process_event(msg)
                    if (data.decode('utf-8').split(' ')[0] == 'append'):
                        #TODO: rewrite everything
                        append_msg = data.decode('utf-8').split('|||')[0][7:]
                        prev_msg = data.decode('utf-8').split('|||')[1]
                        if prev_msg == get_last_log(self.name):
                            self.append_to_log(append_msg)
                        else:
                            prev_index = int(prev_msg[0])
                            msg = 'repair ' + str(prev_index)
                            self.send_direct_msg(msg, self.currLeader)
                    if (data.decode('utf-8').split(' ')[0] == 'repair'):
                        index = int(data.decode('utf-8').split(' ')[1])
                        msg = 'log ' + get_log_at(self.name, index)
                        #send back the message
                        pass
                    if (data.decode('utf-8').split(' ')[0] == 'log'):
                        msg = data.decode('utf-8').split(' ')[4:]
                        if msg != 'finish':
                            self.repair_log(msg)

            #timeout, start election
            except socket.timeout:
                print('Timeout!')
                self.start_election()
    
    def repair_log(self, msg):
        msg = json.loads(msg)
        prev_index = msg['prev'][0]
        prev_log = get_log_at(self.name, prev_index)
        if prev_log == msg['prev']:
            #overwrite curr
            #send next request
            pass
        else:
            #repair the log
            pass

    def get_client(self,val):
        for key, value in self.clientPorts.items():
            if val == value:
                return key
    
    def process_event(self, msg):
        last_log = get_last_log(self.name)
        log_message = str(self.currentTerm) + ' ' + msg
        self.append_to_log(log_message)
        new_message = 'append ' + log_message + '|||' + last_log
        self.broadcast_to_all(new_message)

    #redirect first, then the leader broadcast it

    def create_group(self, members):
        group_id, public_key, private_key = create_new_group(self.name)
        for key,value in members.items():
            pub_key = self.public_keys[key]
            members[key] = encrypt_message(private_key, pub_key)

        log_entry = f'create///{group_id}///{members}///{public_key}'
        if self.role == 'leader':
            self.process_event(log_entry)
        else:
            self.send_direct_msg('redirect ' + log_entry, self.currLeader)
        

    #TODO: kick a member
    def kick_member(self, group_id, member):
        pass

    #TODO: add a member
    def add_member(self, group_id, member):
        member_list = member.split(',')
        members = {x:None for x in member_list}
        for key,value in members.items():
            pub_key = self.public_keys[key]
            # members[key] = encrypt_message(private_key, pub_key)
        log_entry = f'create///{group_id}///{members}'
        if self.role == 'leader':
            self.process_event(log_entry)
        else:
            self.send_direct_msg('redirect ' + log_entry, self.currLeader)
        

    #TODO: print a groups
    def print_groups(self, group_id):
        pass

    #TODO: write message to a group
    def write_message(self, group_id, message):
        pass

    
    def startGUI(self):
        sg.theme('DarkAmber')   # Add a touch of color
        # All the stuff inside your window.
        clients = ['A', 'B', 'C', 'D', 'E']
        buttons = []
        for c in clients:
            if c != self.name:
                buttons.append(sg.Checkbox(c, default=False, key=c))
        buttons.append(sg.Button('Create Group'))
        layout = [  buttons,
                    [sg.Text('Group_id: '), sg.InputText(do_not_clear=False, size=(5,5), key='id1'),sg.Text("Client: "), sg.InputText(do_not_clear=False, size=(10,5), key='c1'), sg.Button('Kick')],
                    [sg.Text('Group_id: '), sg.InputText(do_not_clear=False, size=(5,5), key='id2'),sg.Text("Client: "), sg.InputText(do_not_clear=False, size=(10,5), key='c2'), sg.Button('Add')],
                    [sg.Text('Group_id: '), sg.InputText(do_not_clear=False, size=(5,5), key='id3'), sg.Button('Print Group')],
                    [sg.Text('Group_id: '), sg.InputText(do_not_clear=False, size=(5,5), key='id4'),sg.Text("Message: "), sg.InputText(do_not_clear=False, key='mes'), sg.Button('Write Message')],
                    [sg.Text('Client: '), sg.InputText(do_not_clear=False, size=(5,5), key='c3'), sg.Button('FailLink')],
                ]

        # Create the Window
        window = sg.Window('Client {}'.format(self.name), layout)
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
                break
            if event == 'Create Group':
                members = {self.name: None}
                for c in clients:
                    if c != self.name and values[c] == True:
                        members[c] = None
                self.create_group(members)
            if event == 'Kick':
                group_id = values['id1']
                client_id = values['c1']
                self.kick_member(group_id, client_id)

            if event == 'Add':
                group_id = values['id2']
                client_id = values['c2']
                self.add_member(group_id, client_id)

            if event == 'Print Group':
                group_id = values['id3']
                self.print_groups(group_id)
                
            if event == 'Write Message':
                group_id = values['id4']
                message = values['mes']
                self.write_message(group_id, message)

            if event == 'FailLink':
                client_id = values['c3']
                if client_id != self.name and client_id not in self.fail_clients:
                    self.fail_clients.append(client_id)

        window.close()

if __name__ == "__main__":
     
    clientName = sys.argv[1]
    print(f'The client name is "{clientName}"')
    c1 = myClient(clientName)

    c1.ServerSocket.close()