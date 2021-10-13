import time, psutil, sys, json
from datetime import datetime

EXECUTABLE = sys.argv[1]
USERNAME = sys.argv[2]
QAWA_OUTFILE = sys.argv[3]
MEM_OUTFILE = f"{QAWA_OUTFILE[:-4]}-mem.out"


stack = ""
procedures = {}
min_rss = 0
max_rss = 0
i = 0


def get_new_lines():
    with open(QAWA_OUTFILE , "r") as file_out:
        global i
        lines = file_out.readlines()[i:]
        i += len(lines)
        return lines

def determine_current_procedure(lines):
    global stack
    for line in lines:
        if line.strip().startswith('->'):
            stack += f" {line.split()[2]}({line.split()[4]})"
        if line.strip().startswith('<-'):
            stack = stack.rsplit(' ', 1)[0]
   
def get_rss(p):
    return p.memory_info().rss/1024**3



with open(MEM_OUTFILE , "w") as f:
    f.write('RUNNING\n') 

while True:
    procs = psutil.process_iter(['pid', 'name', 'username'])
    my_procs = [p for p in procs if 
        p.info['name'] == EXECUTABLE and 
        p.info['username'] == USERNAME]

    if not my_procs:
        # f.write('.')
        break
        
    for p in my_procs:
        new_lines = get_new_lines()
        determine_current_procedure(new_lines)
        
        rss = get_rss(p)

        if stack in procedures:
            procedures[stack]["min"] = min(procedures[stack]["min"], rss)
            procedures[stack]["max"] = max(procedures[stack]["max"], rss)
            procedures[stack]["count"] = procedures[stack]["count"] + 1
        else:
            procedures[stack] = {"min": rss, "max": rss, "count": 1}


    # time.sleep(1)


with open(MEM_OUTFILE , "w") as file_memory:
    for key in procedures.keys():
        min = procedures[key]["min"]
        max = procedures[key]["max"]
        count = procedures[key]["count"]
        file_memory.write(f"{key} {min} {max} {count}\n")

