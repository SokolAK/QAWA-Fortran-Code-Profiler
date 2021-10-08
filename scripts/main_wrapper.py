import os
from scripts.logger import log
from scripts.utils import *
from scripts.line_utils import *

FILENAME = os.path.basename(__file__)
FILES = []


def run(CONFIGURATION):
    log('Running', level='info', source=FILENAME)
    
    path = CONFIGURATION['MAIN_FILE']
    process(path)
    

def process(path):
    filename = path.split('/')[-1]
    filename = filename.split('\\')[-1]
    log('Processing ' + filename, level='detail', source=FILENAME)

    lines = read_file(path, strip=False)

    with open(path, 'w') as f:

        i = 0
        while i < len(lines) and is_declaration(filename, lines, i):
            f.write(lines[i])
            i += 1
        
        add_qawa_start(f, filename)

        while i < len(lines):
            if lines[i].strip().lower() == 'end':
                add_qawa_end(f, filename)
            f.write(lines[i])
            i += 1


def add_qawa_start(f, filename):
    f.write(f"      call qawafcp_start('{filename}', 'MAIN', 'M')\n")


def add_qawa_end(f, filename):
    f.write(f"      call qawafcp_end('{filename}', 'MAIN', 'M')\n")