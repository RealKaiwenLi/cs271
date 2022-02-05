from _thread import *
import time
import socket
import os
import sys

class myClient:
    def __init__(self, clientName, clientIP, clientPort) -> None:
        self.x = 3
        self.name = clientName
        self.host = clientIP
        self.port = clientPort
        self.ServerSocket = socket.socket()
        self.clientPorts = {'A': 1111, 'B': 2222, 'C': 3333, 'D': 4444}
        self.clinetIPs = {'A': '127.0.0.1', 'B': '127.0.0.1', 'C': '127.0.0.1', 'D': '127.0.0.1'}

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



    
if __name__ == "__main__":
     
    clientName = sys.argv[1]
    thePorts = {'A': 1111, 'B': 2222, 'C': 3333, 'D': 4444}
    print(f'The client name is "{clientName}"')
    c1 = myClient(clientName, '127.0.0.1', thePorts[clientName])
    c1.Connect_to_older_clients()
    
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