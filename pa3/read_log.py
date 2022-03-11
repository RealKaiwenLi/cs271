#Get the last log entry
def get_last_log(name):
    with open(name + '.txt', 'rb') as f:
        log = f.read()
        next = 0
        index = 0
        term = 0
        while index < len(log):
            idx = log[index:index+1].decode()
            term = idx
            event = log[index+1:index+2].decode()
            group_id = log[index+2:index+4].decode()
            #create event
            if event == '0':
                serial_pub_key = log[index+4:index+4+97]
                mem_number = log[index+101:index+102].decode()
                index += 102
                key_set = {}
                for i in range(0,int(mem_number)):
                    key_set[log[5+i:5+i+1].decode()] = log[5+int(mem_number) + i*256:5+int(mem_number) + i*256 + 256]
                    index += 257
            #add event
            if event == '1':
                index += 257+4
            #kick event
            if event == '2':
                serial_pub_key = log[index+4:index+4+97]
                mem_number = log[index+101:index+102].decode()
                index += 102
                key_set = {}
                for i in range(0,int(mem_number)):
                    key_set[log[5+i:5+i+1].decode()] = log[5+int(mem_number) + i*256:5+int(mem_number) + i*256 + 256]
                    index += 257
            #write event
            if event == '3':
                index += 21
            
            next += 1

        return term, next

def get_log_at(name, num):
    with open(name + '.txt') as f:
        try:
            lines = f.readlines()
            x = {"cur": lines[num-1], "prev": lines[num-2] if num > 1 else "0 0"}
            return x
        except:
            return "finish"


lines = ""
with open('A.txt', 'rb') as f:
    lines = f.read()

# print(len(lines))
# print(get_next_term('A'))
