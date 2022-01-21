import socket
from _thread import *
import PySimpleGUI as sg
import blockChain
import time

class Client(object):
    def __init__(self, addr):
        self.addr = addr
        self.event_num = 0
        self.client_number = 1
        assign_client_num = 0
        self.clients = {}
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSocket.bind(self.addr)
        self.blockchain = blockChain.Blockchain()
        total_clients = 3
        for i in range(total_clients):
            data, client = self.clientSocket.recvfrom(1024)
            assign_client_num += 1
            print("Client {} connected:".format(assign_client_num), client)
            client_info = str(assign_client_num) + "|" + str(total_clients-assign_client_num) + "|" + str(self.clients)
            self.clientSocket.sendto(client_info.encode(), client)
            self.clients[client] = assign_client_num
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
                elif data[2] == "balance":
                    balance = self.check_balance(int(data[1]))
                    self.event_num += 1
                    self.clientSocket.sendto("{} {} balance {}".format(self.event_num, self.client_number, balance).encode(), client)
                elif data[2] == "transfer":
                    res = self.start_transaction(int(data[1]), int(data[3]), int(data[4]))
                    self.event_num += 1
                    self.clientSocket.sendto("{} {} transaction {}".format(self.event_num, self.client_number, res).encode(), client)
                    
    def check_balance(self, id):
        balance = self.blockchain.balance(id)
        return balance
    
    def start_transaction(self, from_id, to_id, amount):
        res = self.blockchain.insert(from_id, to_id, amount)
        return res

    def reply(self,data, client):
        req = data
        self.event_num = max(self.event_num,int(req[0]))
        print("New event number: {}".format(self.event_num))
        self.event_num += 1
        self.clientSocket.sendto('{} {} reply {} '.format(self.event_num, self.client_number, req[1]).encode(), client)
    
    def start(self):
        start_new_thread(self.recv, ())
        self.startGUI()

    def startGUI(self):
        sg.theme('DarkAmber')   # Add a touch of color
        # All the stuff inside your window.
        layout = [  [sg.Button('Print')]]

        # Create the Window
        window = sg.Window('BlockChain Master'.format(self.client_number), layout, size=(250, 100))
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
                break
            if event == 'Print':
                self.blockchain.Show()

        window.close()

if __name__ == '__main__':
    print("Server started")
    client = Client(('127.0.0.1', 4000))
    client.start()
