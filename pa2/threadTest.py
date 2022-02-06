from _thread import *
import time
import socket
import os
import sys
from copy import deepcopy
from time import sleep

class myClient:
    def __init__(self, clientName, clientIP, clientPort) -> None:
        self.x = 3
        self.name = clientName
        self.host = clientIP
        self.port = clientPort
        self.ServerSocket = socket.socket()
        self.clientPorts = {'A': 1111, 'B': 2222, 'C': 3333, 'D': 4444}
        self.clinetIPs = {'A': '127.0.0.1', 'B': '127.0.0.1', 'C': '127.0.0.1', 'D': '127.0.0.1'}
        self.channel = {
                                    'A': {'BA':False, 'DA':False},
                                    'B': {'AB':False,'DB':False},
                                    'C': {'DC':False},
                                    'D': {'BD':False}
                                }
        #sample for client A: {'A': {'BA': False, 'DA': False}, 'B': {'BA': False, 'DA': False}, 'C': {'BA': False, 'DA': False}, 'D': {'BA': False, 'DA': False}}
        #incoming_channel[A][BA] = True means channel BA is recording for the snapshot A. If a message is received on channel BA, it will be appended to state[A]['channels']['BA']
        self.incoming_channel = {
                                    'A': deepcopy(self.channel[self.name]),
                                    'B': deepcopy(self.channel[self.name]), 
                                    'C': deepcopy(self.channel[self.name]), 
                                    'D': deepcopy(self.channel[self.name])
                                }
        # marker_num[A] represents the number of markers received for the snapshot initiated by A
        self.marker_num = {'A': 0,'B': 0,'C': 0,'D': 0}
        self.balance = 10
        #state[A] represents the snapshot record initiated by A
        self.state = {
                        'A':{'balance': 10, 'channels': {x:[] for x in self.channel[self.name]}},
                        'B':{'balance': 10, 'channels': {x:[] for x in self.channel[self.name]}},
                        'C':{'balance': 10, 'channels': {x:[] for x in self.channel[self.name]}},
                        'D':{'balance': 10, 'channels': {x:[] for x in self.channel[self.name]}}
                    }
        try:
            self.ServerSocket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))


        print('Waitiing for a Connection..')
        self.ServerSocket.listen(5) 


    
    def get_connection(self,connection):
 
        connection.send(str.encode('Welcome to the Server'))
        while True:
            data = connection.recv(2048)
            reply = 'The server in threadTest Says: ' + data.decode('utf-8') + "The great"
            if not data:
                break
            connection.sendall(str.encode(reply))
        connection.close()


    
    def initiate_connection(self, host, port):
        ClientSocket = socket.socket()
        print('Waiting for connection')
        try:
            ClientSocket.connect((host, port))
        except socket.error as e:
            print(str(e))

        Response = ClientSocket.recv(1024)
        while True:
            Input = input(f'Say Something to {port} \n')
            ClientSocket.send(str.encode(Input))
            Response = ClientSocket.recv(1024)
            print(Response.decode('utf-8'))
        ClientSocket.close()


    def Connect_to_older_clients(self):
        src = ord(self.name)
        des = 65
        while des != src :
            
            desName = chr(des)
            desIP = self.clinetIPs[desName]
            desPort = self.clientPorts[desName]
            print(f'connection from {self.name} to {desName} on {desIP}:{desPort} ')
            start_new_thread(self.initiate_connection, (desIP,desPort))
            des+=1
            
    def send_message(msg):
        pass


    #save the current state of the client
    def save_state(self, initiator):
        self.state[initiator]['balance'] = self.balance

    #initiate the snapshot
    def init_snapshot(self):
        self.save_state(self.name)
        #send marker to all outgoing channels with initiator

        #start recording on all incoming channels
        self.incoming_channel[self.name] = {x:True for x in self.channel[self.name]}
        
    # handle the state when receving a marker
    def recv_marker(self, sender, initiator):
        if self.marker_num[initiator] == 0 and initiator != self.name:
            #save local state for this initiator
            self.save_state(initiator)
            #send marker to all outgoing channels with initiator

            self.marker_num[initiator] += 1
            #mark channel c is empty
            channel_name = sender + self.name
            self.state[initiator]['channels'][channel_name] = []
            #saving mess on all other incoming channels
            self.incoming_channel[initiator] = {x:True for x in self.channel[self.name]}
            self.incoming_channel[initiator][sender+self.name] = False
        else:
            #stop saving on that channel
            self.incoming_channel[initiator][sender+self.name] = False
            self.marker_num[initiator] += 1
        #if it receivers all markers
        if self.marker_num[initiator] == len(self.channel[self.name]):
            print(self.incoming_channel)
            print(self.state)
            #send the state to initiator

            #reset marker_num
            self.marker_num[initiator] = 0
            #reset state
            self.state[initiator] = {'balance': 10, 'channels': {x+self.name:[] for x in self.channel[self.name]}}

    #append the message to state if recording
    def append_message(self, sender, msg):
        channel_name = sender + self.name
        for initiator,values in self.incoming_channel.items():
            for channel,value in values.items():
                if channel == channel_name and value == True:
                    self.state[initiator]['channels'][channel_name].append(msg)
    
if __name__ == "__main__":
     
    clientName = sys.argv[1]
    thePorts = {'A': 1111, 'B': 2222, 'C': 3333, 'D': 4444}
    print(f'The client name is "{clientName}"')
    c1 = myClient(clientName, '127.0.0.1', thePorts[clientName])
    c1.Connect_to_older_clients()
    c1.recv_marker('B', 'C')
    sleep(1)
    c1.append_message('D', 'hello')
    c1.recv_marker('D', 'C')
    #Waiting to get connection from other clients, we can terminate
    #this while loop when all connections are sat up
    
    ThreadCount = 0
    while True:
        Client, address = c1.ServerSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        start_new_thread(c1.get_connection, (Client, ))
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount))
    c1.ServerSocket.close()