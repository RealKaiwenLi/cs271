from _thread import *
from ast import While
from calendar import c
import time
import socket
import os
import sys
from time import sleep
import PySimpleGUI as sg
import json
from datetime import datetime

class myClient:
    def __init__(self, clientName, clientIP, clientPort) -> None:
        self.name = clientName
        self.host = clientIP
        self.port = clientPort
        self.role = 'follower'
        self.currentTerm = 0
        self.currLeader = None
        self.votedFor = None
        self.log = open(clientName + '.txt', 'a')
        self.votes_received = 0
        self.sent_length = 0
        self.ack_length = 0
        self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ServerSocket.settimeout(2)
        self.clientPorts = {'A': 1111, 'B': 2222, 'C': 3333, 'D': 4444, 'E': 5555}
        self.clinetIPs = '127.0.0.1'

        try:
            self.ServerSocket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))
        time.sleep(5)
        start_new_thread(self.send_heartbeat, ())
        start_new_thread(self.listen_to_all,())
        while True:
            continue
    
    def send_heartbeat(self):
        while True:
            if self.role == 'leader':
                self.broadcast_to_all(f'heartbeat {self.name} {self.currentTerm}')
                sleep(0.5)
    
    def get_last_log(self):
        with open(self.name + '.txt') as f:
            try:
                for line in f:
                    pass
                last_line = line
            except:
                last_line = '0 0'
            return last_line

    def start_election(self):
        self.currentTerm += 1
        self.role = 'candidate'
        print("Set as candidate for term: ", self.currentTerm)
        #TODO:get the latest log
        last_log = self.get_last_log()
        #TODO:Generate RequestVote RPC
        msg = f'RequestVote {self.name} {self.currentTerm} {last_log}'
        #TODO:send request vote to all
        self.broadcast_to_all(msg)
    
    def process_request_vote(self, msg):
        msg_list = msg.split(' ')
        
        pass
        
    def broadcast_to_all(self, msg):
        
        for item in self.clientPorts:
            if item != self.name:
                self.ServerSocket.sendto(str.encode(msg), (self.clinetIPs, self.clientPorts[item]))
                
    def listen_to_all(self):
        print(f'client {self.name} is listening now')
        while True:
            try:
                data, addr = self.ServerSocket.recvfrom(1024) # buffer size is 1024 bytes
                print(data.decode('utf-8'))
                if (data.decode('utf-8').split(' ')[0] == 'RequestVote'):
                    self.process_request_vote(data.decode('utf-8'))
            except socket.timeout:
                print('Timeout!')
                self.start_election()

    
    def send_direct_msg(self, msg, receiver):
        sleep(3)
        self.ServerSocket.sendto(str.encode(msg), (self.clinetIPs[receiver], self.clientPorts[receiver]))

    def get_client(self,val):
        for key, value in self.clientPorts.items():
            if val == value:
                return key
    
if __name__ == "__main__":
     
    clientName = sys.argv[1]
    thePorts = {'A': 1111, 'B': 2222, 'C': 3333, 'D': 4444, 'E': 5555}
    print(f'The client name is "{clientName}"')
    c1 = myClient(clientName, '127.0.0.1', thePorts[clientName])

    c1.ServerSocket.close()