from http import server
import socket
from _thread import *
import PySimpleGUI as sg
import ast

class Client(object):
    def __init__(self):
        self.event_num = 0
        self.client_number = 1
        self.job = []
        self.in_critical_section = False
        self.reply_num = 0
        self.clients = {}
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server = ('0.0.0.0', 4000)
        self.clients[self.server] = 1
        self.clientSocket.sendto("I am a new client".encode(), self.server)
        data, client = self.clientSocket.recvfrom(1024)
        print("Client 1 connected:", client)
        # print(data.decode())
        data = data.decode().split("|")
        self.client_number = int(data[0])
        clients = ast.literal_eval(data[2])
        for client in clients:
            self.clients[client] = clients[client]
            self.clientSocket.sendto("I am client {}".format(self.client_number).encode(), client)
            print("Client {} connected:".format(self.clients[client]), client)
        for i in range(int(data[1])):
            data, client = self.clientSocket.recvfrom(1024)
            client_num = data.decode().split(" ")[3]
            print("Client {} connected: ".format(client_num), client)
            self.clients[client] = int(client_num)
        # print(self.clients)
    
    def recv(self):
        while True:
            data, client = self.clientSocket.recvfrom(1024)
            if data:
                print("Received from client {}: {}".format(data.decode().split(' ')[1],data.decode()))
                data = data.decode().split(' ')
                if data[2] == "request":
                    #check queue
                    self.reply(data,client)
                elif data[2] == "reply":
                    self.reply_num += 1
                    if (self.reply_num == len(self.clients)):
                        print("All replies received, transcation started")
                        self.in_critical_section = True
                        self.reply_num = 0
                        #start transaction
                        self.event_num += 1
                        self.clientSocket.sendto("{} {} {}".format(self.event_num,str(self.client_number), self.job[1]).encode(), self.server)
                        self.in_critical_section = False
                        self.job = []

    def reply(self,data, client):
        req = data
        self.event_num = max(self.event_num,int(req[0]))
        print("New event number: {}".format(self.event_num))
        self.event_num += 1
        if not self.in_critical_section:
            self.clientSocket.sendto('{} {} reply {} '.format(self.event_num, self.client_number, req[1]).encode(), client)
    
    def start(self):
        start_new_thread(self.recv, ())
        self.startGUI()

    def startGUI(self):
        sg.theme('DarkAmber')   # Add a touch of color
        # All the stuff inside your window.
        layout = [  [sg.Button('Check balance')],
                    [sg.Text('Transfer: '), sg.InputText(do_not_clear=False), ],
                    [sg.Text('Amount: '), sg.InputText(do_not_clear=False)],
                    [sg.Button('Submit'), sg.Button('Cancel')] ]

        # Create the Window
        window = sg.Window('Client {}'.format(self.client_number), layout)
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
                break
            if event == 'Check balance':
                self.event_num += 1
                self.job = ["{} {}".format(self.event_num, self.client_number),"balance"]
                for client in self.clients:
                    print("Message sent to client {}".format(self.clients[client]))
                    self.clientSocket.sendto("{} {} request balance".format(self.event_num,str(self.client_number)).encode(), client)
            else:
                self.event_num += 1
                self.job = ["{} {}".format(self.event_num, self.client_number),"transfer {} {}".format(values[0],values[1])]
                for client in self.clients:
                    print("Message sent to client {}".format(self.clients[client]))
                    self.clientSocket.sendto("{} {} request transaction".format(self.event_num,str(self.client_number)).encode(), client)

        window.close()


if __name__ == '__main__':
    print("Client 3 started")
    client = Client()
    client.start()


