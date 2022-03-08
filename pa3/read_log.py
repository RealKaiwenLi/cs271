#Get the last log entry
def get_last_log(name):
    with open(name + '.txt') as f:
        try:
            i = 0
            for line in f:
                i+=1
                pass
            last_line = str(i) + ' ' + line
        except:
            last_line = '0 0'
        return last_line

def get_log_at(name, num):
    with open(name + '.txt') as f:
        try:
            lines = f.readlines()
            x = {"cur": lines[num-1], "prev": lines[num-2] if num > 1 else "0 0"}
            return x
        except:
            return "finish"