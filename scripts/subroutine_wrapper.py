import os
from scripts.logger import log
from scripts.utils import *
from scripts.line_utils import *

FILENAME = os.path.basename(__file__)
FILES = []


def run(CONFIGURATION):
    log('Running', level='info', source=FILENAME)
    
    FILES = prepare_file_list(CONFIGURATION['SOURCE_DIR'], CONFIGURATION['SUBROUTINES_FILES'])
    for f in FILES:
        process(f)
    

def process(path):
    prepare_file(path)
    filename = path.split('/')[-1]
    filename = filename.split('\\')[-1]
    log('Processing ' + filename, level='detail', source=FILENAME)

    lines = read_file(path, strip=False)
    
    with open(path, 'w') as f:

        i = 0
        while i < len(lines):

            line = lines[i]
            line = remove_pure(line)

            if is_subroutine_call(line):
                
                procedure_name = get_procedure_name(line)
                tab = get_leading_tab(line)
                
                add_qawa_start(f, tab, filename, procedure_name)

                f.write(line)

                j = i
                prev_line = line.strip()
                while j + 1 < len(lines):

                    next_line = lines[j+1]

                    prev_line_is_broken = prev_line.strip().endswith('&')
                    prev_line_is_comment = is_comment(filename, prev_line)
                    next_line_is_continuation = next_line.strip().startswith('&') or next_line.strip().startswith('$') or next_line.strip().startswith('>')
                    next_line_is_comment = is_comment(filename, next_line)

                    if prev_line_is_broken or next_line_is_continuation or next_line_is_comment:
                        f.write(next_line)
                        j += 1
                        if not next_line_is_comment:
                            prev_line = next_line
                    else:
                        i = j
                        break

                add_qawa_end(f, tab, filename, procedure_name)


            else:
                f.write(line)

            i += 1


def remove_pure(line):
    if line.lower().lstrip().startswith('pure'):
        pure_position = line.find('pure')
        tab = get_separator(' ', pure_position - 1)
        line = tab + line[pure_position + 4:]
    return line


def is_subroutine_call(line):
    return line.lstrip().lower().startswith('call ')


def get_procedure_name(line):
    procedure_name = line[:line.find('(')]
    procedure_name = procedure_name[line.lower().find('call')+4:]
    procedure_name = procedure_name.strip()
    return procedure_name


def get_leading_tab(line):
    return line[0 : len(line)-len(line.lstrip())]


def add_qawa_start(f, tab, filename, procedure_name):
    f.write(f"{tab}call qawafcp_start('{filename}', '{procedure_name}', 'S')\n")


def add_qawa_end(f, tab, filename, procedure_name):
    f.write(f"{tab}call qawafcp_end('{filename}', '{procedure_name}', 'S')\n")