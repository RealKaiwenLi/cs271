from _thread import *
from ast import While
from calendar import c
import time
import socket
import os
import sys
from copy import deepcopy
from time import sleep
import PySimpleGUI as sg

class myClient:
    def __init__(self, clientName, clientIP, clientPort) -> None:
        self.x = 3
        self.name = clientName
        self.host = clientIP
        self.port = clientPort
        self.balance = 10
        self.broadcast_flag = False
        self.broadcast_msg = ""
        self.outgoing_channels_flag = False
        self.ServerSocket = socket.socket() 
        self.clientPorts = {'A': 1111, 'B': 2222, 'C': 3333, 'D': 4444}
        self.clinetIPs = {'A': '127.0.0.1', 'B': '127.0.0.1', 'C': '127.0.0.1', 'D': '127.0.0.1'}
        self.clientSocekt={'A':0, 'B': 0, 'C':0 , 'D':0}
        self.outgoing_channels = {'A':['B'] , 'B':['A','D'] , 'C':['B'], 'D':['A','B','C']}
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


    
    # def get_connection(self,connection):
 
    #     connection.send(str.encode('Welcome to the Server'))
    #     while True:
    #         data = connection.recv(2048)
    #         reply = 'The server in threadTest Says: ' + data.decode('utf-8') + "The great"
    #         if not data:
    #             break
    #         connection.sendall(str.encode(reply))
    #     connection.close()

    # def initiate_connection(self, host, port):
    #     ClientSocket = socket.socket()
    #     print('Waiting for connection')
    #     try:
    #         ClientSocket.connect((host, port))
    #     except socket.error as e:
    #         print(str(e))
        
    #     return ClientSocket
        #Response = ClientSocket.recv(1024)
        # currentClient = True
       
        # while True:
        #     # Input = input(f'Say Something to {port} \n')
        #     if self.broadcast_flag == True:
        #         if currentClient == True:
        #             #send the message for this round 
        #             print("entered broadcast flag == true")
        #             ClientSocket.send(str.encode(self.broadcast_msg))
        #             currentClient = False
                    
        #     else:
        #         currentClient = True
        #         print("current client true again")
            
    
        #     Response = ClientSocket.recv(1024)
        #     print(Response.decode('utf-8'))
                

        # ClientSocket.close()

    def Connect_to_older_clients(self):
        src = ord(self.name)
        des = 65
        while des != src :
            
            desName = chr(des)
            desIP = self.clinetIPs[desName]
            desPort = self.clientPorts[desName]
            print(f'connection from {self.name} to {desName} on {desIP}:{desPort} ')
            self.clientSocekt[desName] = self.initiate_connection(desIP,desPort)
            des+=1

    def broadcast_to_all(self, msg):
        
        for item in self.clientPorts:
            if item != self.name:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(str.encode(msg), (self.clinetIPs[item], self.clientPorts[item]))
                
    def listen_to_all(self):
        print(f'client {self.name} is listening now')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.bind((self.clinetIPs[self.name], self.clientPorts[self.name]))
 
        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            print(data.decode('utf-8'))
            message_type = data.decode('utf-8').split()
            if(message_type[0] == "Transfer"):
                #call append_message
                self.balance += int(message_type[1])
            elif message_type == "MARKER":
                #call recv_marker
                pass

        
    
    def send_direct_msg(self, msg, receiver):
    
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(str.encode(msg), (self.clinetIPs[receiver], self.clientPorts[receiver]))

    def send_outgoing_channels(self, msg):
        des = self.outgoing_channels[self.name]
        for item in des:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(str.encode(msg), (self.clinetIPs[item], self.clientPorts[item]))


    # def listening (self, soc):
    #     while True:
    #         data = soc.recv(2048)
    #         reply = 'The server ' + clientName + " says: "+  data.decode('utf-8') + " The great"
    #         if not data:
    #             break
    #         soc.sendall(str.encode(reply))


    #save the current state of the client
    def save_state(self, initiator):
        self.state[initiator]['balance'] = self.balance

    #initiate the snapshot
    def init_snapshot(self):
        self.save_state(self.name)
        #send marker to all outgoing channels with initiator
        #TODO --> broadcast to all outgoing channel send a string "MARKER self.name"
        self.broadcast_to_all("MARKER " + self.name)
        #start recording on all incoming channel
        self.incoming_channel[self.name] = {x:True for x in self.channel[self.name]}
        
    # handle the state when receving a marker
    def recv_marker(self, sender, initiator):
        if self.marker_num[initiator] == 0 and initiator != self.name:
            #save local state for this initiator
            self.save_state(initiator)
            #TODO "marker initiaior name" send marker to all outgoing channels
            self.send_outgoing_channels("MARKER "+ initiator)

            self.marker_num[initiator] += 1
            #mark channel c is empty
            channel_name = sender + self.name
            self.state[initiator]['channels'][channel_name] = []
            #saving mess on all other incoming channels
            self.incoming_channel[initiator] = {x:True for x in self.channel[self.name]}
            self.incoming_channel[initiator][channel_name] = False
        else:
            self.incoming_channel[initiator][sender+self.name] = False
            self.marker_num[initiator] += 1
        #if it receivers all markers
        if self.marker_num[initiator] == len(self.channel[self.name]):
            print(self.incoming_channel)
            print(self.state)
            #send the state to initiator. self.state[initiator]
            #TODO : send above value to the initiator of snapshot
            self.send_direct_msg(self.state[initiator], initiator)
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


    def startGUI(self):
        sg.theme('DarkAmber')   # Add a touch of color
        # All the stuff inside your window.
        layout = [  [sg.Button('Snapshot')],
                    [sg.Button('Balance')],
                    [sg.Text('Transfer: '), sg.InputText(do_not_clear=False), ],
                    [sg.Text('Amount: '), sg.InputText(do_not_clear=False)],
                    [sg.Button('Submit'), sg.Button('Cancel')] ]

        # Create the Window
        window = sg.Window('Client {}'.format(self.name), layout)
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
                break
            if event == 'Snapshot':
                self.init_snapshot()
            elif event == "Balance":
                print(self.balance)
            else: # submit values[0] the reciver and values[1] for the amount
                TheReceiver = values[0]
                amount = int(values[1])
                if TheReceiver in self.outgoing_channels[self.name]:
                    if(amount > 0 or amount < self.balance):
                        self.send_direct_msg("Transfer " + str(amount), TheReceiver)
                    else:
                        print("The amount of money you want ot transfer is invalid")
                else:
                    print("Not connected to that client for money transfer")
               

        window.close()
    
if __name__ == "__main__":
     
    clientName = sys.argv[1]
    thePorts = {'A': 1111, 'B': 2222, 'C': 3333, 'D': 4444}
    print(f'The client name is "{clientName}"')
    c1 = myClient(clientName, '127.0.0.1', thePorts[clientName])
    start_new_thread(c1.listen_to_all,())

    time.sleep(2)

    # c1.send_outgoing_channels("A message from:" + c1.name )
    


    
    # c1.Connect_to_older_clients()
    #Waiting to get connection from other clients, we can terminate
    #this while loop when all connections are sat up
    
    # ThreadCount = 0
    # current = ord(c1.name) -64
    # for i in range(0 ,4 - current):
    #     index = ((current + i ) % 4 ) + 65
    #     c1.clientSocekt[chr(index)], address = c1.ServerSocket.accept()
    #     print('Connected to: ' + address[0] + ':' + str(address[1]))
    #     # start_new_thread(c1.get_connection, (c1.clientSocekt[chr(index)], ))
    #     ThreadCount += 1
    #     print('Thread Number: ' + str(ThreadCount))
        

    # for item in c1.clientSocekt:
    #     print(c1.clientSocekt[item])

    # if c1.name == 'C':
    #     c1.broadcast_to_all("hi everybody")


    # for item in c1.clientSocekt:
    #     if item != c1.name:
    #         temp = c1.clientSocekt[item]
    #         start_new_thread(c1.listening,(temp,))

    c1.startGUI()
    c1.ServerSocket.close()