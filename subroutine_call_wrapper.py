import os
from strings import *
from utils import *
from line_utils import *
import re

class Subroutine_call_wrapper():
    def __init__(self, SCRIPT_DIR, SOURCE_DIR, OUT_FILE, FILES, SUBROUTINES, MAIN_FILE):
        self.SOURCE_DIR = SOURCE_DIR
        self.SCRIPT_DIR = SCRIPT_DIR
        self.FILES = FILES
        self.SUBROUTINES = SUBROUTINES
        self.OUT_FILE = OUT_FILE
        self.MAIN_FILE = MAIN_FILE


    def wrap(self):
        FILES = prepare_file_list(self.SOURCE_DIR, self.FILES)
        for f in FILES:
            self.process(f)


    def process(self, filename):
        path = f"{self.SOURCE_DIR}{filename}"
        if not filename in self.MAIN_FILE:
            prepare_file(path)
        filename = path.split('/')[-1]
        filename = filename.split('\\')[-1]
        # log('Processing ' + filename, level='detail', source=FILENAME)

        lines = read_file(path)
        
        with open(path, 'w') as f:

            i = 0

            while i < len(lines):

                line = lines[i]
                line = self.remove_pure(line)

                if self.is_subroutine_call(line):
                    
                    procedure_name = self.get_procedure_name(line)

                    if (procedure_name in self.SUBROUTINES or ('*' in self.SUBROUTINES and f"-{procedure_name}" not in self.SUBROUTINES)):
                    
                        tab = self.get_leading_tab(line)
                        
                        self.add_qawa_start(f, filename, procedure_name, 'S')

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

                        self.add_qawa_end(f, filename, procedure_name, 'S')

                        # print(filename, procedure_name, 'wrapped')
                    else:
                        f.write(line)
                    
                else:
                    f.write(line)

                i += 1

            if filename in self.MAIN_FILE:
                self.add_qawa_start_procedure(f, filename, self.SCRIPT_DIR, self.OUT_FILE)
                self.add_qawa_end_procedure(f, filename, self.SCRIPT_DIR, self.OUT_FILE)


    def remove_pure(self, line):
        if line.lower().lstrip().startswith('pure'):
            pure_position = line.find('pure')
            tab = get_separator(' ', pure_position - 1)
            line = tab + line[pure_position + 4:]
        return line


    def is_subroutine_call(self, line):
        return line.lstrip().lower().startswith('call ')


    def get_procedure_name(self, line):
        procedure_name = line[:line.find('(')]
        procedure_name = procedure_name[line.lower().find('call')+4:]
        procedure_name = procedure_name.strip()
        return procedure_name


    def get_leading_tab(self, line):
        return line[0 : len(line)-len(line.lstrip())]


    def add_qawa_start(self, f, filename, name, typ):
        f.write(f"      call qawa_S('{filename}', '{name}', '{typ}')\n")


    def add_qawa_end(self, f, filename, name, typ):
        f.write(f"      call qawa_E('{filename}', '{name}', '{typ}')\n")    


    def add_qawa_start_procedure(self, f, filename, script_dir, out_file):
        body = get_qawa_start_procedure(script_dir, out_file)
        if filename.endswith('.f90'):
            body = convert_text_block_from_f77_to_f90(body)
        f.write(body)


    def add_qawa_end_procedure(self, f, filename, script_dir, out_file):
        body = get_qawa_end_procedure(script_dir, out_file)
        if filename.endswith('.f90'):
            body = convert_text_block_from_f77_to_f90(body)
        f.write(body)