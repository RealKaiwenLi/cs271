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
                self.broadcast_to_all(f'heartbeat {self.name} {self.currentTerm}'.encode())

    #start election
    def start_election(self):
        self.update_current_term(self.currentTerm + 1)
        self.role = 'candidate'
        print("Set as candidate for term: ", self.currentTerm)
        trm, idx = get_last_log(self.name)
        last_log = f'{idx} {trm}'
        self.votes_received = 1
        self.update_voted_for(self.name)
        msg = f'RequestVote {self.name} {self.currentTerm} {last_log}'
        self.broadcast_to_all(msg.encode())
    
    def complete_log(self, index, term):
        trm, idx = get_last_log(self.name)
        return (term > int(trm)) or ((term == int(trm)) and index >= int(idx))
    
    def process_request_vote(self, msg):
        msg_list = msg.split(' ')
        term = int(msg_list[2])
        log_ok = self.votedFor == None or self.complete_log(int(msg_list[3]), int(msg_list[4]))
        term_ok = term > self.currentTerm or (term == self.currentTerm and (self.votedFor == None or self.votedFor == msg_list[1]))
        if log_ok and term_ok:
            self.update_current_term(term)
            self.role = 'follower'
            self.update_voted_for(msg_list[1])
            self.send_direct_msg(f'Vote {self.name} {self.currentTerm}'.encode(), msg_list[1])

    def broadcast_to_all(self, msg):
        for item in self.clientPorts:
            if item != self.name and item not in self.fail_clients:
                self.ServerSocket.sendto(msg, (self.clinetIPs, self.clientPorts[item]))
                sleep(0.5)
        
    def send_direct_msg(self, msg, receiver):
        if receiver not in self.fail_clients:
            self.ServerSocket.sendto(msg, (self.clinetIPs, self.clientPorts[receiver]))
                
    def listen_to_all(self):
        print(f'client {self.name} is listening now')
        while True:
            try:
                data, addr = self.ServerSocket.recvfrom(4096*10)
                client = self.get_client(addr[1])
                #use first byte to identify
                if client not in self.fail_clients:
                    if (data[0:1] == b'h'):
                        self.role = 'follower'
                        self.currLeader = client
                        if self.currentTerm > int(data.decode('utf-8').split(' ')[2]):
                            self.send_direct_msg(f'g {self.currentTerm} {self.currLeader}'.encode(), self.currLeader)
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
                    
                    if (data[0:1] == b'd'):
                        msg = data[1:]
                        self.process_event(msg)
                    if (data[0:1] == b'a'):
                        msg = data[1:]
                        self.update_entries(msg)
                    
                    if (data[0:1] == b'g'):
                        msg = data.decode().split(' ')
                        if self.role != 'follower':
                            print('step down')
                            self.role = 'follower'
                            self.currentTerm = int(msg[1])
                            self.currLeader = msg[2]

            #timeout, start election
            except socket.timeout:
                print('Timeout!')
                self.start_election()

    def get_client(self,val):
        for key, value in self.clientPorts.items():
            if val == value:
                return key

    def process_append_entries(self, msg):
        print('entry appended!')
        with open(self.name + '.txt', 'ab') as f:
            f.write(msg)
    
    def update_entries(self, msg):
        print('entry appended!')
        with open(self.name + '.txt', 'wb') as f:
            f.write(msg)

    def process_event(self, msg):
        self.process_append_entries(msg)
        with open(self.name + '.txt', 'rb') as f:
            msg = f.read()
        tmp = [b'a', msg]
        self.broadcast_to_all(b''.join(tmp))

    def create_group(self, members):

        log_entry = encrypt_group_key(self.name, self.currentTerm, members, '0')
        if self.role == 'leader':
            self.process_event(log_entry)
        else:
            tmp = [b'd', log_entry]
            self.send_direct_msg(b''.join(tmp), self.currLeader)    

    def kick_member(self, group_id, member):
        log = kick_member(self.name, self.currentTerm, group_id, member)
        print(f"kick {member} from group {group_id}")
        if type(log) == str:
            print(log)
        else:
            print(f'add {member} to group {group_id}')
            if self.role == 'leader':
                self.process_event(log)
            else:
                tmp = [b'd', log]
                self.send_direct_msg(b''.join(tmp), self.currLeader)

    def add_member(self, group_id, member):
        log = add_member(self.name, self.currentTerm, group_id, member)
        if type(log) == str:
            print(log)
        else:
            print(f'add {member} to group {group_id}')
            if self.role == 'leader':
                self.process_event(log)
            else:
                tmp = [b'd', log]
                self.send_direct_msg(b''.join(tmp), self.currLeader)
        

    def print_groups(self, group_id):
        group = read_message(self.name, group_id)
        print(f'members: {group["members"].keys()}\n messages: {group["messages"]}')

    def write_message(self, group_id, message):
        log = write_message(self.name, self.currentTerm, group_id, message)
        print(f'write {message} to group {group_id}')
        if self.role == 'leader':
            self.process_event(log)
        else:
            tmp = [b'd', log]
            self.send_direct_msg(b''.join(tmp), self.currLeader)

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
                    [sg.Text('Client: '), sg.InputText(do_not_clear=False, size=(5,5), key='c4'), sg.Button('FixLink')],
                ]

        # Create the Window
        window = sg.Window('Client {}'.format(self.name), layout)
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
                break
            if event == 'Create Group':
                members = self.name
                for c in clients:
                    if c != self.name and values[c] == True:
                        members += c
                
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
                print('print group', group_id)
                self.print_groups(group_id)
                
            if event == 'Write Message':
                group_id = values['id4']
                message = values['mes']
                self.write_message(group_id, message)

            if event == 'FailLink':
                client_id = values['c3']
                if client_id != self.name and client_id not in self.fail_clients:
                    self.fail_clients.append(client_id)
            
            if event == 'FixLink':
                client_id = values['c4']
                if client_id != self.name and client_id in self.fail_clients:
                    self.fail_clients.remove(client_id)

        window.close()

if __name__ == "__main__":
     
    clientName = sys.argv[1]
    print(f'The client name is "{clientName}"')
    c1 = myClient(clientName)

    c1.ServerSocket.close()