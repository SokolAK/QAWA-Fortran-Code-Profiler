import os
from qawa_utils import *
from qawa_strings import *

class Main_wrapper():
    def __init__(self, SCRIPT_DIR, MAIN_FILE, OUT_FILE):
        self.MAIN_FILE = MAIN_FILE
        self.MAIN_FILE_NAME = os.path.basename(MAIN_FILE)
        self.SCRIPT_DIR = SCRIPT_DIR
        self.OUT_FILE = OUT_FILE


    def get_before_fragment(self):
        fragment = f""" 
      {get_fragment_header()}
      real :: start, end
      real ( kind = 8 ) :: wtime, wtime2
      wtime = omp_get_wtime()
      call cpu_time(start)

      !$OMP CRITICAL
      open(61,file=
     $'{self.SCRIPT_DIR}
     $/outs/
     ${self.OUT_FILE}',
     $action='write')
      write(61,'(A,I2,A2,I2)') '-> {self.MAIN_FILE_NAME} MAIN M',
     $OMP_GET_THREAD_NUM()+1, '/', OMP_GET_NUM_THREADS()
      close(61)
      !$OMP END CRITICAL
      {get_fragment_footer()}

"""

        if self.MAIN_FILE.lower().rstrip().endswith('.f90'):
            fragment = convert_text_block_from_f77_to_f90(fragment)
        
        return fragment


    def get_after_fragment(self):
        fragment = f""" 
      {get_fragment_header()}
      call cpu_time(end)
      wtime2 = omp_get_wtime()
    
      !$OMP CRITICAL
      open(61,file=
     $'{self.SCRIPT_DIR}
     $/outs/
     ${self.OUT_FILE}',
     $action='write',position='append')
      write(61,'(A,2F14.6)') '<- {self.MAIN_FILE_NAME} MAIN M',
     $end-start, wtime2-wtime
      close(61)
      !$OMP END CRITICAL
      {get_fragment_footer()}

"""

        if self.MAIN_FILE.lower().rstrip().endswith('.f90'):
            fragment = convert_text_block_from_f77_to_f90(fragment)
        
        return fragment


    def add_before_fragment(self, lines):
        i = 0
        while is_declaration(self.MAIN_FILE, lines, i):
            i += 1
        lines[i:i] = self.get_before_fragment()

    
    def add_after_fragment(self, lines):
        j = len(lines) - 1
        while j > 0:
            line = lines[j].lstrip().lower()
            if line.startswith('stop') or line.startswith('end'):
                lines[j:j] = self.get_after_fragment()
                break
            j -= 1


    def add_use_declarations(self, lines):
        i = 0
        while not lines[i].lstrip().lower().startswith('program'):
            i += 1
        lines[i+1:i+1] = '      use omp_lib\n'


    def wrap(self):
        prepare_file(self.MAIN_FILE)

        lines = []
        with open(self.MAIN_FILE, 'r') as f:
            lines = f.readlines()

        self.add_before_fragment(lines)
        self.add_after_fragment(lines)
        self.add_use_declarations(lines)

        with open(self.MAIN_FILE, 'w') as f:
            for line in lines:
                f.write(line)
