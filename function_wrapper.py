import os
from strings import *
from utils import *
import re

class Function_wrapper():
    def __init__(self, SCRIPT_DIR, SOURCE_DIR, OUT_FILE, FILES, FUNCTIONS):
        self.SOURCE_DIR = SOURCE_DIR
        self.SCRIPT_DIR = SCRIPT_DIR
        self.FILES = FILES
        self.FUNCTIONS = FUNCTIONS
        self.OUT_FILE = OUT_FILE


    class Function():
        def __init__(self, file, name):
            self.file = file
            self.name = name
        def __str__(self):
            return f"{self.file:20s} {self.name:20s}"


    def wrap(self):
        files = prepare_file_list(self.SOURCE_DIR, self.FILES)
        for file in files:
            lines = read_file(f"{self.SOURCE_DIR}/{file}")
            functions = self.find_functions(file, lines)
            for function in functions:
                print(f"{file:20s}{function.name:20s}", end='', flush=True)
                self.wrap_function(file, lines, function)
                print('wrapped')

            save_file(f"{self.SOURCE_DIR}/{file}", lines)


    def find_functions(self, file, lines):
        functions = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if self.should_wrap(file, lines, i):
                name = get_procedure_name_from_line(line)
                functions.append(self.Function(file,name))
            i += 1
        return functions


    def should_wrap(self, file, lines, i):
        line = lines[i]
        return not is_comment(file, line) and \
            self.is_function_start(file, line) and \
            (get_procedure_name_from_line(line) in self.FUNCTIONS or \
                ('*' in self.FUNCTIONS and f"-{get_procedure_name_from_line(line)}" not in self.FUNCTIONS)) and \
            not self.is_wrapped_function(lines, i)


    def wrap_function(self, file, lines, function):
        prepare_file(f"{self.SOURCE_DIR}/{function.file}")
        i = self.find_function(file, lines, function)

        while is_broken_line(lines, i):
            i += 1
        i += 1
        lines.insert(i, '      use omp_lib\n')

        while is_declaration(function.file,lines,i):
            i += 1

        lines.insert(i, self.get_before_fragment(function))

        while not 'end function' in lines[i].lower() and \
                not ('end' in lines[i].lower() and \
                'return' in lines[i-1].lower()):

            if lines[i].strip().lower() == 'return':
                lines.insert(i, self.get_after_fragment(function))
                i += 1
            if i + 1 == len(lines):
                break
            i += 1

        if 'end function' in lines[i].lower():
            lines.insert(i, self.get_after_fragment(function))


    def find_function(self, file, lines, function):
        i = 0
        while not (self.is_function_start(file, lines[i]) and \
                function.name == get_procedure_name_from_line(lines[i])):
            i += 1
        return i


    def is_function_start(self, file, line):
        return not is_comment(file, line) and not 'end' in line.lower()+' ' and 'function ' in line.lower()


    def is_wrapped_function(self, lines, i):
        return True if 'qawa wrapped function' in lines[i-1] else False


    def get_before_fragment(self, function):
        fragment= f"""
{get_fragment_header(f"open_{get_prefix()}{function.name}")}
      real ( kind = 8 ) :: cpu_start, cpu_end, wtime_start, wtime_end
      wtime_start = omp_get_wtime()
      call cpu_time(cpu_start)
      !$OMP CRITICAL
      open(61,file=
     $'{self.SCRIPT_DIR}
     $/outs/
     ${self.OUT_FILE}',
     $action='write',position='append')
      write(61,'(A,I2,A2,I2)')
     $'-> {function.file}
     $ {function.name} F',
     $OMP_GET_THREAD_NUM()+1, '/', OMP_GET_NUM_THREADS()
      close(61)
      !$OMP END CRITICAL
{get_fragment_footer()}

"""
        if is_f90_format(function.file):
            fragment = convert_text_block_from_f77_to_f90(fragment)
        
        return fragment
        

    def get_after_fragment(self, function):
        fragment= f"""
{get_fragment_header(f"close_{get_prefix()}{function.name}")}
      call cpu_time(cpu_end)
      wtime_end = omp_get_wtime()
      !$OMP CRITICAL
      open(61,file=
     $'{self.SCRIPT_DIR}
     $/outs/
     ${self.OUT_FILE}',
     $action='write',position='append')
      write(61,'(A,2F14.6)')
     $'<- {function.file}
     $ {function.name} F',
     $cpu_end-cpu_start, wtime_end-wtime_start
      close(61)
      !$OMP END CRITICAL
{get_fragment_footer()}

"""
        if is_f90_format(function.file):
            fragment = convert_text_block_from_f77_to_f90(fragment)
        
        return fragment