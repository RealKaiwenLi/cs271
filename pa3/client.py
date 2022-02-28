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
        self.private_key = get_private_key(clientName)
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
        while True:
            continue

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
    
    #Get the last log entry
    def get_last_log(self):
        with open(self.name + '.txt') as f:
            try:
                for line in f:
                    pass
                last_line = line
            except:
                last_line = '0 0'
            return last_line

    #start election
    def start_election(self):
        self.update_current_term(self.currentTerm + 1)
        self.role = 'candidate'
        print("Set as candidate for term: ", self.currentTerm)
        last_log = self.get_last_log()
        self.votes_received = 1
        self.update_voted_for(self.name)
        #TODO: Is there any other parameter to send?
        msg = f'RequestVote {self.name} {self.currentTerm} {last_log}'
        self.broadcast_to_all(msg)
    
    def complete_log(self, index, term):
        log = self.get_last_log().split(' ')
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
            if item != self.name:
                self.ServerSocket.sendto(str.encode(msg), (self.clinetIPs, self.clientPorts[item]))
                sleep(0.5)
        
    def send_direct_msg(self, msg, receiver):
        self.ServerSocket.sendto(str.encode(msg), (self.clinetIPs, self.clientPorts[receiver]))
                
    def listen_to_all(self):
        print(f'client {self.name} is listening now')
        while True:
            try:
                data, addr = self.ServerSocket.recvfrom(1024) # buffer size is 1024 bytes
                print(data.decode('utf-8'))
                if (data.decode('utf-8').split(' ')[0] == 'heartbeat'):
                    self.role = 'follower'
                    self.currentTerm = max(int(data.decode('utf-8').split(' ')[2]), self.currentTerm)

                if (data.decode('utf-8').split(' ')[0] == 'RequestVote'):
                    self.process_request_vote(data.decode('utf-8'))

                if (data.decode('utf-8').split(' ')[0] == 'Vote'):
                    self.votes_received += 1
                    if self.votes_received > len(self.clientPorts) / 2 and self.role == 'candidate':
                        self.role = 'leader'
                        self.currLeader = self.name
                        print(f'I am the leader now')
                        self.ServerSocket.settimeout(None)
            #timeout, start election
            except socket.timeout:
                print('Timeout!')
                self.start_election()

    def get_client(self,val):
        for key, value in self.clientPorts.items():
            if val == value:
                return key
    
    def create_group(self, members):
        group_id, private_key = create_new_group(self.name)
        for member in members:
            #encrypt group id and private key
            #send to each member
            pass
        #append to log


if __name__ == "__main__":
     
    clientName = sys.argv[1]
    print(f'The client name is "{clientName}"')
    c1 = myClient(clientName)

    c1.ServerSocket.close()