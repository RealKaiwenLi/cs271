import json
c = ['A', 'B', 'C', 'D', 'E']
for i in c:
    state = open(f'{i}_state.txt')
    states = state.readlines()
    state.close()

    new_state = json.loads(states[0])
    new_state['currentTerm'] = 0
    new_state['votedFor'] = None
    states[0] = json.dumps(new_state)+'\n'
    state = open(f'{i}_state.txt','w')
    new_file_contents = "".join(states)
    state.write(new_file_contents)
    state.close()

    state = open(f'{i}.txt', 'wb')
    state.close()

