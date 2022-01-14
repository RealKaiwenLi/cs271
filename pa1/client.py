import socket
from _thread import *
from multiprocessing import Process
import multiprocessing, platform
import PySimpleGUI as sg

def startGUI(client):
    sg.theme('DarkAmber')   # Add a touch of color
    # All the stuff inside your window.
    layout = [  [sg.Text('Some text on Row 1')],
                [sg.Text('Enter something on Row 2'), sg.InputText()],
                [sg.Button('Ok'), sg.Button('Cancel')] ]

    # Create the Window
    window = sg.Window('Window Title', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
            break
        print('You entered ', values[0])

    window.close()

if __name__ == '__main__':
    if platform.system() == "Darwin":
        multiprocessing.set_start_method('spawn')
    clientsocket = socket.socket()
    host = "127.0.0.1"
    port = 5555

    print("waiting for connections...")

    try:
        clientsocket.connect((host, port))
    except socket.error as e:
        print(str(e))

    res = clientsocket.recv(1024)
    print(res.decode())

    p = Process(target=startGUI, args=(clientsocket,))
    p.start()
    
    while True:
        
        res = clientsocket.recv(1024)
        print(res.decode())

    clientsocket.close()


