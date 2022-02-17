from copy import deepcopy
name = 'A'
channel = {
                                    'A': {'B':True, 'D':False},
                                    'B': {'A':False,'D':False},
                                    'C': {'D':False},
                                    'D': {'B':False}
                                }
incoming_channel = {
                            'A': deepcopy(channel[name]),
                            'B': deepcopy(channel[name]), 
                            'C': deepcopy(channel[name]), 
                            'D': deepcopy(channel[name])
                        }

for initiator,values in incoming_channel.items():
    for channel,value in values.items():
        if value == True:
            print(initiator,channel)


# print(incoming_channel)

# initiator = 'A'
# sender = 'B'
# name = 'C'


# channel_name = sender + name
# state[initiator]['channels'][channel_name] = ''

# print(state)