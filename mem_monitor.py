import time, psutil, sys, json
from datetime import datetime

EXECUTABLE = sys.argv[1]
USERNAME = sys.argv[2]
OUTFILE = sys.argv[3]

max_rss = 0


with open("/home/adam.sokol/QCHEM/PROFILING/QAWA/outs/qawa-mem.out", "w") as f:
    f.write('START\n') 

while True:
    procs = psutil.process_iter(['pid', 'name', 'username'])
    my_procs = [p for p in procs if 
        p.info['name'] == EXECUTABLE and 
        p.info['username'] == USERNAME]

    if not my_procs:
        # f.write('.')
        break
    for p in my_procs:
        # f.write(str(p.info['name']) + '\n')
        # f.write(str(time.time()) + '\n')
        # f.write(str(p.as_dict()['create_time']) + '\n')
        # f.write(str(datetime.fromtimestamp(p.as_dict()['create_time'])) + '\n')
        # f.write(str(p.memory_info().rss/1024**3) + '\n')  
        max_rss = max(max_rss, p.memory_info().rss/1024**3)
        # f.write('\n' + str(max_rss)) 


    with open("/home/adam.sokol/QCHEM/PROFILING/QAWA/outs/qawa-mem.out", "a") as file_memory:
        with open(OUTFILE , "r") as file_out:
            lines = file_out.read().splitlines()
            last_line = lines[-1]
            file_memory.write(f'{last_line}\n') 


    # time.sleep(1)


with open("/home/adam.sokol/QCHEM/PROFILING/QAWA/outs/qawa-mem.out", "a") as file_memory:
    file_memory.write(f'{max_rss}\n') 
    file_memory.write('END\n') 

