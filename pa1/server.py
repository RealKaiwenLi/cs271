import socket
from _thread import *

serversocket = socket.socket()
my_clients = []

host = "127.0.0.1"
port = 5555
thread_count = 0

try:
    serversocket.bind((host, port))
except socket.error as e:
    print(str(e))

print("Server started on port " + str(port))
print("Waiting for connections...")
serversocket.listen(5)

def client_thread(conn):
    conn.send(str("welcome to server").encode())
    my_clients.append(conn)
    while True:
        data = conn.recv(2048)
        if not data:
            break
        print("Received: " + data.decode())
        for client in my_clients:
            client.sendall(data)
    conn.close()

while True:
    client,address = serversocket.accept()
    print("New Client connected to: " + str(address[0]) + ":" + str(address[1]))
    start_new_thread(client_thread, (client,))
    thread_count += 1
    print("Thread count: " + str(thread_count))
serversocket.close()


