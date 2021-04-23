import os
from utils import *
from line_utils import *
from strings import *

class Main_wrapper():
    def __init__(self, SCRIPT_DIR, MAIN_FILE, OUT_FILE):
        self.MAIN_FILE = MAIN_FILE
        self.MAIN_FILE_NAME = os.path.basename(MAIN_FILE)
        self.SCRIPT_DIR = SCRIPT_DIR
        self.OUT_FILE = OUT_FILE


    def wrap(self):
        prepare_file(self.MAIN_FILE)

        lines = []
        with open(self.MAIN_FILE, 'r') as f:
            lines = f.readlines()

        self.add_before_fragment(lines)
        self.add_after_fragment(lines)
        self.add_use_declarations(lines)

        save_file(self.MAIN_FILE, lines)
 

    def add_before_fragment(self, lines):
        i = 0
        while is_declaration(self.MAIN_FILE, lines, i):
            i += 1
        lines.insert(i, self.get_before_fragment())

    
    def add_after_fragment(self, lines):
        j = len(lines) - 1
        last_line = True
        while j > 0:
            line = lines[j].lstrip().lower()
            #if line.startswith('stop') or line.startswith('end'):
            if line.startswith('stop') or line.startswith('end program') or \
                    (line.strip() == 'end' and last_line):
                lines.insert(j, self.get_after_fragment())

            if not is_comment(self.MAIN_FILE, line):
                last_line = False
            j -= 1


    def add_use_declarations(self, lines):
        i = 0
        while not lines[i].lstrip().lower().startswith('program'):
            i += 1
        lines.insert(i+1, '      use omp_lib\n')


    def get_before_fragment(self):
        fragment = \
f""" {get_fragment_header(f"open_{get_prefix()}main")}
{get_wrapper_declarations(self.SCRIPT_DIR, self.OUT_FILE)}
{get_wrapper_time_start(self.MAIN_FILE_NAME, 'MAIN', 'M', file_mode="")}
{get_fragment_footer()}

"""

        if self.MAIN_FILE.lower().rstrip().endswith('.f90'):
            fragment = convert_text_block_from_f77_to_f90(fragment)
        return fragment


    def get_after_fragment(self):
        fragment = \
f""" {get_fragment_header(f"close_{get_prefix()}main")}
{get_wrapper_time_end(self.MAIN_FILE_NAME, 'MAIN', 'M')}
{get_fragment_footer()}

"""

        if self.MAIN_FILE.lower().rstrip().endswith('.f90'):
            fragment = convert_text_block_from_f77_to_f90(fragment)
        return fragment
