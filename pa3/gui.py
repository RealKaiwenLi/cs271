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
                [sg.Text('Group_id: '), sg.InputText(do_not_clear=False, size=(5,5)),sg.Text("Client: "), sg.InputText(do_not_clear=False, size=(10,5)), sg.Button('Kick')],
                [sg.Text('Group_id: '), sg.InputText(do_not_clear=False, size=(5,5)),sg.Text("Client: "), sg.InputText(do_not_clear=False, size=(10,5)), sg.Button('Add')],
                [sg.Text('Group_id: '), sg.InputText(do_not_clear=False, size=(5,5)), sg.Button('Read Message')],
                [sg.Text('Group_id: '), sg.InputText(do_not_clear=False, size=(5,5)),sg.Text("Message: "), sg.InputText(do_not_clear=False), sg.Button('Write Message')] 
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
            pass
        if event == 'Add':
            pass
        if event == 'Read Message':
            pass
        if event == 'Write Message':
            pass

    window.close()

startGUI('D')