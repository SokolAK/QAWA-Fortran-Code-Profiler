import os
from strings import *
from ordered_set import OrderedSet
from utils import *
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


    def add_line(self, lines, i, str):
        lines.insert(i, str + '\n')
        return i + 1


    def add_wrapper(self, lines, i, wrapper):
        for line in wrapper.splitlines():
            i = self.add_line(lines, i, line)
        return i


    def is_subroutine_start(self, line):
        return line.lower().strip().startswith('subroutine')


    def is_wrapper(self, line):
        return line.strip() == get_wrapper_header()


    def is_wrapped_subroutine(self, subroutine):
        return subroutine.startswith(get_prefix())


    def is_subroutine_on_list(self, subroutine):
        return subroutine in self.SUBROUTINES or \
            ('*' in self.SUBROUTINES and f"-{subroutine}" not in self.SUBROUTINES)


    def get_subroutine_name_from_line(self, line):
        return line.strip().replace('(',' ').split()[1]


    def should_wrap(self, file, lines, i):
        line = lines[i]
        return not is_comment(file, line) and \
            self.is_subroutine_start(line) and \
            (get_procedure_name_from_line(line) in self.SUBROUTINES or \
                ('*' in self.SUBROUTINES and f"-{get_procedure_name_from_line(line)}" not in self.SUBROUTINES)) and \
            not self.is_wrapper(lines[i-1]) and \
            not self.is_wrapped_subroutine(get_procedure_name_from_line(line))


    def modify_stops(self):
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self.SOURCE_DIR):
            files += [os.path.join(dirpath, file).replace(self.SOURCE_DIR,'') for file in filenames]
        files = set([file for file in files if file.endswith('.f') or file.endswith('.f90')])

        for file in files:
            lines = read_file(f"{self.SOURCE_DIR}/{file}")

            for i,line in enumerate(lines):
                line = line.lower()
                if line.lstrip().startswith('stop'):

                    lines[i] = line.replace(line[line.index('stop'):], 'return\n')

                    while lines[i].strip().endswith('&') or \
                        lines[i+1].strip().startswith('$') or lines[i+1].strip().startswith('&'):
                        lines[i+1] = ''
                        i += 1

            save_file(f"{self.SOURCE_DIR}/{file}", lines)

                        
    def modify_ends(self, lines, subroutines):
        for i, line in enumerate(lines):
            if 'end subroutine' in line.lower():
                words = line.strip().split()
                if len(words) == 3:
                    name = line.strip().split()[2]
                    for subroutine in subroutines:
                        if subroutine.name.lower() == name.lower():
                            lines[i] = line.replace(name, f"{get_prefix()}{name}")


    def find_subroutine(self, lines, subroutine):
        i = 0
        while not (self.is_subroutine_start(lines[i]) and \
                subroutine.name == self.get_subroutine_name_from_line(lines[i])):
            i += 1
        return i


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


    def find_subroutines(self, file, lines):
        subroutines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if self.should_wrap(file, lines, i):
                name = self.get_subroutine_name_from_line(line)

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


    def prepare_subroutine_wrapper(self, subroutine):
        wrapper_body = \
f"""{get_wrapper_header()}
{subroutine.signature_lines}
      use omp_lib
{subroutine.declarations_lines}
      real :: start, end
      real ( kind = 8 ) :: wtime, wtime2
      wtime = omp_get_wtime()
      call cpu_time(start)

      !$OMP CRITICAL
      open(61,file=
     $'{self.SCRIPT_DIR}
     $/outs/
     ${self.OUT_FILE}',
     $action='write',position='append')
      write(61,'(A,I2,A2,I2)')
     $'-> {subroutine.file} {subroutine.name} S',
     $OMP_GET_THREAD_NUM()+1, '/', OMP_GET_NUM_THREADS()
      close(61)
      !$OMP END CRITICAL

      call {get_prefix()}{subroutine.signature_lines.replace('subroutine','').replace('Subroutine','').replace('SUBROUTINE','').lstrip()}
      call cpu_time(end)
      wtime2 = omp_get_wtime()
    
      !$OMP CRITICAL
      open(61,file=
     $'{self.SCRIPT_DIR}
     $/outs/
     ${self.OUT_FILE}',
     $action='write',position='append')
      write(61,'(A,2F14.6)')
     $'<- {subroutine.file} {subroutine.name} S',
     $end-start, wtime2-wtime
      close(61)
      !$OMP END CRITICAL

      return
      end
{get_wrapper_footer()}

"""

        if subroutine.file.lower().rstrip().endswith('.f90'):
            wrapper_body = convert_text_block_from_f77_to_f90(wrapper_body)
        
        return wrapper_body
        
