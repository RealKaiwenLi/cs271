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
        self.job = []
        assign_client_num = 1
        self.in_critical_section = False
        self.reply_num = 0
        self.clients = {}
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSocket.bind(self.addr)
        self.blockchain = blockChain.Blockchain()
        total_clients = 3
        for i in range(total_clients - 1):
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
                elif data[2] == "reply":
                    self.reply_num += 1
                    if (self.reply_num == len(self.clients)):
                        print("All replies received, transcation started")
                        self.in_critical_section = True
                        self.reply_num = 0
                        #start transaction
                        self.event_num += 1
                        if self.job[1] == "balance":
                            res = "Balance: "
                            res += str(self.check_balance(1))
                        else:
                            res = "Transaction: "
                            res = self.start_transaction(1,int(self.job[1].split(' ')[1]),int(self.job[1].split(' ')[2]))
                        print(res)
                        self.in_critical_section = False
                        self.job = []
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
        time.sleep(5)
        return balance
    
    def start_transaction(self, from_id, to_id, amount):
        res = self.blockchain.insert(from_id, to_id, amount)
        if res == "succeed":
            print("Current blockchain:")
            self.blockchain.Show()
        return res

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
    print("Client 1 started")
    client = Client(('127.0.0.1', 4000))
    client.start()
