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
import json

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
        self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientPorts = {'A': 1111, 'B': 2222, 'C': 3333, 'D': 4444}
        self.clinetIPs = {'A': '127.0.0.1', 'B': '127.0.0.1', 'C': '127.0.0.1', 'D': '127.0.0.1'}
        self.clientSocekt={'A':0, 'B': 0, 'C':0 , 'D':0}
        self.outgoing_channels = {'A':['B'] , 'B':['A','D'] , 'C':['B'], 'D':['A','B','C']}
        self.channel = {
                                    'A': {'BA':False, 'DA':False},
                                    'B': {'AB':False, 'CB': False, 'DB':False},
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

    def broadcast_to_all(self, msg):
        
        for item in self.clientPorts:
            if item != self.name:
                self.ServerSocket.sendto(str.encode(msg), (self.clinetIPs[item], self.clientPorts[item]))
                
    def listen_to_all(self):
        print(f'client {self.name} is listening now')
 
        while True:
            data, addr = self.ServerSocket.recvfrom(1024) # buffer size is 1024 bytes
            print(data.decode('utf-8'))
            message_type = data.decode('utf-8').split()
            sender = self.get_client(int(addr[1]))
            if(message_type[0] == "Transfer"):
                self.append_message(sender, data.decode('utf-8'))
                self.balance += int(message_type[1])
            elif message_type[0] == "MARKER":
                self.recv_marker(sender, message_type[1])
                pass
            else:
                # print(data.decode('utf-8'))
                pass

        
    
    def send_direct_msg(self, msg, receiver):
        sleep(3)
        self.ServerSocket.sendto(str.encode(msg), (self.clinetIPs[receiver], self.clientPorts[receiver]))

    def send_outgoing_channels(self, msg):
        sleep(3)
        des = self.outgoing_channels[self.name]
        for item in des:
                self.ServerSocket.sendto(str.encode(msg), (self.clinetIPs[item], self.clientPorts[item]))

    #save the current state of the client
    def save_state(self, initiator):
        self.state[initiator]['balance'] = self.balance

    #initiate the snapshot
    def init_snapshot(self):
        self.save_state(self.name)
        #send marker to all outgoing channels with initiator
        #TODO --> broadcast to all outgoing channel send a string "MARKER self.name"
        self.send_outgoing_channels("MARKER " + self.name)
        #start recording on all incoming channel
        self.incoming_channel[self.name] = {x:True for x in self.channel[self.name]}
        
    def get_client(self,val):
        for key, value in self.clientPorts.items():
            if val == value:
                return key
    
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
            print('ALl marker received')
            #send the state to initiator. self.state[initiator]
            #TODO : send above value to the initiator of snapshot
            state_message = json.dumps(self.state[initiator])
            self.send_direct_msg(self.name + ': ' + state_message, initiator)
            #reset marker_num
            self.marker_num[initiator] = 0
            #reset state
            self.state[initiator] = {'balance': 10, 'channels': {x:[] for x in self.channel[self.name]}}

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
                    if(amount > 0 and amount < self.balance):
                        self.balance -= amount
                        self.send_direct_msg("Transfer " + str(amount), TheReceiver)
                        print("Success")
                    else:
                        print("Incorrect")
                else:
                    print("Incorrect")
               

        window.close()
    
if __name__ == "__main__":
     
    clientName = sys.argv[1]
    thePorts = {'A': 1111, 'B': 2222, 'C': 3333, 'D': 4444}
    print(f'The client name is "{clientName}"')
    c1 = myClient(clientName, '127.0.0.1', thePorts[clientName])
    start_new_thread(c1.listen_to_all,())

    

    c1.startGUI()
    c1.ServerSocket.close()