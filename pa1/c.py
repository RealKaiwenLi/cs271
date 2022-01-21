from http import server
import socket
from _thread import *
import PySimpleGUI as sg
import ast
from time import sleep
import pymsgbox

class Client(object):
    def __init__(self):
        self.event_num = 0
        self.client_number = 1
        self.in_critical_section = False
        self.reply_num = 0
        self.balance = 10
        self.clients = {}
        self.queue = []
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server = ('127.0.0.1', 4000)
        self.clientSocket.sendto("I am a new client".encode(), self.server)
        data, client = self.clientSocket.recvfrom(1024)
        print("Server connected:", client)
        # print(data.decode())
        datas = data.decode().split("|")
        self.client_number = int(datas[0])
        clients = ast.literal_eval(datas[2])
        for client in clients:
            self.clients[client] = clients[client]
            self.clientSocket.sendto("I am client {}".format(self.client_number).encode(), client)
            print("Client {} connected:".format(self.clients[client]), client)
        for i in range(int(datas[1])):
            data, client = self.clientSocket.recvfrom(1024)
            print(data.decode())
            client_num = data.decode().split(" ")[3]
            print("Client {} connected: ".format(client_num), client)
            self.clients[client] = int(client_num)
        print("Initial Balance: {}".format(datas[3]))
    
    def recv(self):
        while True:
            data, client = self.clientSocket.recvfrom(1024)
            if data:
                print("Received from client {}: {}".format(data.decode().split(' ')[1],data.decode()))
                data = data.decode().split(' ')
                self.event_num = max(self.event_num,int(data[0]))
                print("New event number: {}".format(self.event_num))
                if data[2] == "request":
                    self.append_queue(data, client)
                    self.reply(data,client)
                elif data[2] == "reply":
                    self.reply_num += 1                 
                elif data[2] == "release":
                    print("Client {} released".format(data[1]))
                    self.queue.pop(0)
                    # print(self.queue)
                elif data[2] == "balance":
                    job = self.queue[0][2]
                    if job[3] == "balance":
                        self.display("Client {} balance: {}".format(self.client_number,data[3]))
                        self.balance = int(data[3])
                        self.event_num += 1
                        self.queue.pop(0)
                        message = "{} {} release".format(self.event_num,str(self.client_number)).encode()
                        self.send_all(message)
                        self.in_critical_section = False
                        # print(self.queue)
                    else:
                        if int(data[3]) < int(job[5]):
                            self.display("INCORRECT, your balance is {}".format(data[3]))
                            self.queue.pop(0)
                            self.event_num += 1
                            message = "{} {} release".format(self.event_num,str(self.client_number)).encode()
                            self.send_all(message)
                            self.in_critical_section = False
                        else:
                            print("Your balance is {}".format(data[3]))
                            self.event_num += 1
                            self.send("{} {} transfer {} {}".format(self.event_num,self.client_number ,self.queue[0][2][4],self.queue[0][2][5]).encode(), self.server)
                elif data[2] == "transaction":
                    self.balance -= int(self.queue[0][2][5])
                    self.queue.pop(0)
                    self.event_num += 1
                    message = "{} {} release".format(self.event_num,str(self.client_number)).encode()
                    self.send_all(message)
                    self.in_critical_section = False
                    print("Your balance is {}".format(self.balance))
                    # print(self.queue)
                
                if self.reply_num == len(self.clients) and self.queue[0][1] == self.client_number and not self.in_critical_section:
                    print("All replies received, transcation started")
                    self.in_critical_section = True
                    #start transaction
                    self.reply_num = 0
                    self.get_balance()

    def display(self, context):
        print(context)

    def get_balance(self):
        sleep(3)
        self.event_num += 1
        self.send("{} {} balance".format(self.event_num,str(self.client_number)).encode(), self.server)

    def reply(self,data, client):
        req = data
        self.event_num += 1
        self.send('{} {} reply {} '.format(self.event_num, self.client_number, req[1]).encode(), client)
    
    def send(self, context, client):
        sleep(3)
        self.clientSocket.sendto(context, client)
    
    def send_all(self, context):
        sleep(3)
        for client in self.clients:
            print("Message sent to client {}".format(self.clients[client]))
            self.clientSocket.sendto(context, client)

    def append_queue(self, data, client):
        number = float(data[0] + '.' + data[1])
        node = (number, client, data)
        self.queue.append(node)
        self.queue = sorted(self.queue, key=lambda x: x[0])
    
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
                message = "{} {} request balance".format(self.event_num,str(self.client_number))
                self.append_queue(message.split(' '), self.client_number)
                self.send_all(message.encode())
            else:
                if int(values[0]) == int(self.client_number) or int(values[0]) > len(self.clients)+1 or int(values[0]) <= 0:
                    self.display("INVALID CLIENT NUMBER")
                else:
                    self.event_num += 1
                    message = "{} {} request transaction {} {}".format(self.event_num,self.client_number,values[0],values[1])
                    self.append_queue(message.split(' '), self.client_number)
                    self.send_all(message.encode())

        window.close()


if __name__ == '__main__':
    client = Client()
    client.start()


