import os
from strings import *
from utils import *
from line_utils import *
import re

class Subroutine_wrapper():
    def __init__(self, SCRIPT_DIR, SOURCE_DIR, OUT_FILE, FILES, SUBROUTINES):
        self.SOURCE_DIR = SOURCE_DIR
        self.SCRIPT_DIR = SCRIPT_DIR
        self.FILES = FILES
        self.SUBROUTINES = SUBROUTINES
        self.OUT_FILE = OUT_FILE


    class Subroutine():
        def __init__(self, file, name, signature, signature_lines, args, declarations_lines):
            self.file = file
            self.name = name
            self.signature = signature
            self.signature_lines = signature_lines
            self.args = args
            self.declarations_lines = declarations_lines
        def __str__(self):
            return f"{self.file:20s} {self.name:20s}"


    def wrap(self):
        files = prepare_file_list(self.SOURCE_DIR, self.FILES)

        for file in files:
            lines = []
            lines = read_file(f"{self.SOURCE_DIR}/{file}")

            subroutines = self.find_subroutines(file, lines)
            for subroutine in subroutines:
                print(subroutine, end='')
                self.wrap_subroutine(lines, subroutine)
                print('wrapped')

            self.modify_ends(lines, subroutines)

            save_file(f"{self.SOURCE_DIR}/{file}",lines)

        self.modify_stops()


    def find_subroutines(self, file, lines):
        subroutines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if self.should_wrap(file, lines, i):
                name = get_procedure_name_from_line(line)

                signature_lines = []
                signature_lines.append(line)
                signature = name + line[line.find('('):].replace('&', '').strip()
                while not signature.endswith(')'):
                    i += 1
                    signature += f"{lines[i].replace('&', '').replace('$','').strip()}"
                    signature_lines.append(lines[i])
                signature_lines = ''.join(signature_lines)

                args = []
                args_str = signature.replace(name,'') \
                    .replace('(', '') \
                    .replace(')', '') \
                    .replace('&', '') \
                    .replace(' ', '')
                args = args_str.split(',')    

                i += 1
                declarations_lines = []
                key_words = get_declaration_key_words()
                end_of_declarations = False
                while is_declaration(file,lines,i):
                    if not is_comment(file, lines[i]):    
                        declarations_lines.append(lines[i])
                    i += 1

                declarations_lines = ''.join(declarations_lines)
                subroutines.append(self.Subroutine(file,name,signature,signature_lines,args,declarations_lines))
            i += 1
        return subroutines


    def should_wrap(self, file, lines, i):
        line = lines[i]
        return not is_comment(file, line) and \
            self.is_subroutine_start(line) and \
            (get_procedure_name_from_line(line) in self.SUBROUTINES or \
                ('*' in self.SUBROUTINES and f"-{get_procedure_name_from_line(line)}" not in self.SUBROUTINES)) and \
            not self.is_wrapper(lines[i-1]) and \
            not self.is_wrapped_subroutine(get_procedure_name_from_line(line)) and \
            not self.is_interface(lines, i)


    def wrap_subroutine(self, lines, subroutine):
        prepare_file(f"{self.SOURCE_DIR}/{subroutine.file}")
        i = self.find_subroutine(lines, subroutine)
        lines[i] = lines[i].replace(subroutine.name, f"{get_prefix()}{subroutine.name}")
        line = lines[i]
        
        splitted_line = line.split('(')
        if len(splitted_line) > 1:
            lines[i] = splitted_line[0]
            lines.insert(i+1, f"({splitted_line[1]}")

            if subroutine.file.strip().endswith('.f'):
                lines[i] = f"{lines[i]}\n"
                lines[i+1] = f"     ${lines[i+1]}"
            if subroutine.file.strip().endswith('.f90'):
                lines[i] = f"{lines[i]}&\n"

        wrapper = self.prepare_subroutine_wrapper(subroutine)
        lines.insert(i, wrapper)


    def find_subroutine(self, lines, subroutine):
        i = 0
        while not (self.is_subroutine_start(lines[i]) and \
                subroutine.name == get_procedure_name_from_line(lines[i])) or \
                self.is_interface(lines, i):
            i += 1
        return i


    def is_subroutine_start(self, line):
        return line.lower().strip().startswith('subroutine')


    def is_wrapper(self, line):
        return line.strip() == get_wrapper_header()


    def is_wrapped_subroutine(self, subroutine):
        return subroutine.startswith(get_prefix())


    def is_interface(self, lines, i):
        if i == 1:
            return False
        if lines[i-1].strip() == 'interface':
            return True
        return False


    def is_subroutine_on_list(self, subroutine):
        return subroutine in self.SUBROUTINES or \
            ('*' in self.SUBROUTINES and f"-{subroutine}" not in self.SUBROUTINES)


    def modify_stops(self):
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self.SOURCE_DIR):
            files += [os.path.join(dirpath, file).replace(self.SOURCE_DIR,'') for file in filenames]
        files = set([file for file in files if file.endswith('.f') or file.endswith('.f90')])

        for file in files:
            lines = read_file(f"{self.SOURCE_DIR}{file}")

            for i,line in enumerate(lines):
                line = line.lower()
                if line.lstrip().startswith('stop'):

                    lines[i] = line.replace(line[line.index('stop'):], 'return\n')

                    while lines[i].strip().endswith('&') or \
                        lines[i+1].strip().startswith('$') or lines[i+1].strip().startswith('&'):
                        lines[i+1] = ''
                        i += 1

            save_file(f"{self.SOURCE_DIR}{file}", lines)

                        
    def modify_ends(self, lines, subroutines):
        for i, line in enumerate(lines):
            if 'end subroutine' in line.lower():
                if i + 1 >= len(lines) or (i + 1 < len(lines) and not lines[i+1].strip() == 'end interface'):
                    words = line.strip().split()
                    if len(words) == 3:
                        name = line.strip().split()[2]
                        for subroutine in subroutines:
                            if subroutine.name.lower() == name.lower():
                                lines[i] = line.replace(name, f"{get_prefix()}{name}")


    def prepare_subroutine_wrapper(self, subroutine):
        wrapper_body = \
f"""{get_wrapper_header()}
{subroutine.signature_lines}
      use omp_lib
{subroutine.declarations_lines}
{get_wrapper_declarations(self.SCRIPT_DIR, self.OUT_FILE)}
{get_wrapper_time_start(subroutine.file, subroutine.name, 'S')}
      call {get_prefix()}{subroutine.signature_lines.replace('subroutine','').replace('Subroutine','').replace('SUBROUTINE','').lstrip()}
{get_wrapper_time_end(subroutine.file, subroutine.name, 'S')}
      return
      end
{get_wrapper_footer()}

"""

        if subroutine.file.lower().rstrip().endswith('.f90'):
            wrapper_body = convert_text_block_from_f77_to_f90(wrapper_body)
        
        return wrapper_body
        
