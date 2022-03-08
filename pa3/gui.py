import PySimpleGUI as sg
def startGUI(client):
    sg.theme('DarkAmber')   # Add a touch of color
    # All the stuff inside your window.
    clients = ['A', 'B', 'C', 'D', 'E']
    buttons = []
    for c in clients:
        if c != client:
            buttons.append(sg.Checkbox(c, default=False, key=c))
    buttons.append(sg.Button('Create Group'))
    layout = [  buttons,
                [sg.Text('Group_id: '), sg.InputText(do_not_clear=False, size=(5,5), key='id1'),sg.Text("Client: "), sg.InputText(do_not_clear=False, size=(10,5), key='c1'), sg.Button('Kick')],
                [sg.Text('Group_id: '), sg.InputText(do_not_clear=False, size=(5,5), key='id2'),sg.Text("Client: "), sg.InputText(do_not_clear=False, size=(10,5), key='c2'), sg.Button('Add')],
                [sg.Text('Group_id: '), sg.InputText(do_not_clear=False, size=(5,5), key='id3'), sg.Button('Print Group')],
                [sg.Text('Group_id: '), sg.InputText(do_not_clear=False, size=(5,5), key='id4'),sg.Text("Message: "), sg.InputText(do_not_clear=False, key='mes'), sg.Button('Write Message')],
                [sg.Text('Client: '), sg.InputText(do_not_clear=False, size=(5,5), key='c3'), sg.Button('FailLink')],
            ]

    # Create the Window
    window = sg.Window('Client {}'.format(client), layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
            break
        if event == 'Create Group':
            if values['A'] == True:
                print('A')
            pass
        if event == 'Kick':
            group_id = values['id1']
            client_id = values['c1']
        if event == 'Add':
            group_id = values['id2']
            client_id = values['c2']
        if event == 'Print Group':
            group_id = values['id3']
            
        if event == 'Write Message':
            group_id = values['id4']
            message = values['mes']
        if event == 'FailLink':
            client_id = values['c3']

    window.close()

startGUI('D')