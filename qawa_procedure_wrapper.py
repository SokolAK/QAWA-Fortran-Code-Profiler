import os
from qawa_strings import *
from ordered_set import OrderedSet
from qawa_utils import *
import re

class Procedure_wrapper():
    def __init__(self, SCRIPT_DIR, SOURCE_DIR, OUT_FILE, FILES, PROCEDURES):
        self.SOURCE_DIR = SOURCE_DIR
        self.SCRIPT_DIR = SCRIPT_DIR
        self.FILES = FILES
        self.PROCEDURES = PROCEDURES
        self.OUT_FILE = OUT_FILE

    class Procedure():
        def __init__(self, file, kind, name, signature, signature_lines, declarations_lines):
            self.file = file
            self.kind = kind
            self.name = name
            self.signature = signature
            self.signature_lines = signature_lines
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

    def prepare_procedure_wrapper(self, procedure):
        i, name = self.get_procedure_name_index_on_line(procedure.signature_lines)
        if procedure.kind == 'subroutine':
            call_string = f"call {get_prefix()}{procedure.signature_lines[i:]}"
        if procedure.kind == 'function':
            result_index = procedure.signature_lines.lower().find('result')
            if result_index > 0:
                result_name = procedure.signature_lines[result_index+7:].rstrip()[:-1]
                call_string = f"{result_name} = {get_prefix()}{procedure.signature_lines[i:result_index].lstrip()}"
            else :
                call_string = f"{procedure.name} = {get_prefix()}{procedure.signature_lines[i:result_index].lstrip()}"

        wrapper_body = \
f"""{get_wrapper_header()}
{procedure.signature_lines}
      use omp_lib
{procedure.declarations_lines}
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
     $'-> {procedure.file} {procedure.name}',
     $OMP_GET_THREAD_NUM()+1, '/', OMP_GET_NUM_THREADS()
      close(61)
      !$OMP END CRITICAL

      {call_string}
      call cpu_time(end)
      wtime2 = omp_get_wtime()
    
      !$OMP CRITICAL
      open(61,file=
     $'{self.SCRIPT_DIR}
     $/outs/
     ${self.OUT_FILE}',
     $action='write',position='append')
      write(61,'(A,2F14.6)')
     $'<- {procedure.file} {procedure.name}',
     $end-start, wtime2-wtime
      close(61)
      !$OMP END CRITICAL

      return
      end
{get_wrapper_footer()}

"""

        if procedure.file.lower().rstrip().endswith('.f90'):
            wrapper_body = convert_text_block_from_f77_to_f90(wrapper_body)
        
        return wrapper_body
        

    def prepare_file_list(self):
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self.SOURCE_DIR):
            files += [os.path.join(dirpath, file).replace(self.SOURCE_DIR,'') for file in filenames]
        files = set([file for file in files if file.endswith('.f') or file.endswith('.f90')])
        #files.update([f for f in listdir(SOURCE_DIR) if isfile(join(SOURCE_DIR, f))])
        files = [f for f in files if f in self.FILES or '*' in self.FILES]
        files = [f for f in files if f"-{f}" not in self.FILES]
        print(f"FILES: {files}")
        return files

    def is_subroutine_start(self, line):
        return line.lower().lstrip().startswith('subroutine')

    def is_function_start(self, line):
        items = line.strip().lower().split()
        if not 'end' in items:
            if (len(items) > 0 and items[0] == 'function') or (len(items) > 1 and items[1] == 'function'):
                return True
        return False

    def is_procedure_start(self, line):
        return self.is_subroutine_start(line) or self.is_function_start(line)

    def is_wrapper(self, line):
        return line.strip() == get_wrapper_header()

    def is_wrapped_procedure(self, procedure):
        return procedure.startswith(get_prefix())

    def is_procedure_on_list(self, procedure):
        pass
        # print(procedure)
        # return f"-{procedure}" not in self.PROCEDURES and \
        #     (procedure in self.PROCEDURES or \
        #     (procedure.kind == 'subroutine' and 's' in self.PROCEDURES) or \
        #     (procedure.kind == 'function' and 'f' in self.PROCEDURES))

    def get_procedure_name_index_on_line(self, line):
        i = 0
        if 'subroutine' in line.lower():
            i = line.lower().find('subroutine') + 10
        if 'function' in line.lower():
            i = line.lower().find('function') + 8
            
        tab = len(line[i:]) - len(line[i:].lstrip())
        i += tab
        line = line[i:]
        iE = line.find('(')
        return i, line[:iE]

        # i = line.find('(')
        # if i > 0:
        #     line = line[:i]
        # line = line.rstrip()
        # i = line.rfind(' ')
        # if i < 0:
        #     return i, None
        # else:
        #     return i+1, line[i+1:]


    def get_procedure_name_from_line(self, line):
        i, name = self.get_procedure_name_index_on_line(line)
        return name
        #return line.strip().replace('(',' ').split()[1]

    def get_result_type_from_line(self, line):
        first_word = line.lstrip().split()[0]
        return first_word if not first_word.lower() in ['function', 'subroutine'] else ''

    def get_procedure_kind_from_line(self, line):
        kinds = ['subroutine', 'function']
        for kind in kinds:
            if kind in line.lower():
                return kind
        return None


    def should_wrap(self, file, lines, i):
        line = lines[i]
        if not is_comment(file, line) and self.is_procedure_start(line):
            if f"-{self.get_procedure_name_from_line(line)}" not in self.PROCEDURES and \
                    (self.get_procedure_name_from_line(line) in self.PROCEDURES or \
                    (self.get_procedure_kind_from_line(line) == 'function' and 'f' in self.PROCEDURES) or \
                    (self.get_procedure_kind_from_line(line) == 'subroutine' and 's' in self.PROCEDURES)):
                #print(self.is_procedure_start(line), self.get_procedure_kind_from_line(line), self.get_procedure_name_from_line(line))
                #print(line)
                if not self.is_wrapper(lines[i-1]) and not self.is_wrapped_procedure(self.get_procedure_name_from_line(line)):
                    return True

        return False


        return not is_comment(file, line) and \
            self.is_procedure_start(line) and \
            f"-{self.get_procedure_name_from_line(line)}" not in self.PROCEDURES and \
            (self.get_procedure_name_from_line(line) in self.PROCEDURES or \
                (self.get_procedure_kind_from_line(line) == 'function' and 'f' in self.PROCEDURES) or \
                (self.get_procedure_kind_from_line(line) == 'subroutine' and 's' in self.PROCEDURES)) and \
            not self.is_wrapper(lines[i-1]) and \
            not self.is_wrapped_procedure(self.get_procedure_name_from_line(line))


    def process_line(self, file, lines, i):
        if self.should_wrap(file,lines,i):
            procedure = get_procedure_from_line(line)
            print(f"{file:20s}            {procedure:20s}", end='')
            if self.is_procedure_on_list(procedure):
                j = i + 1
                while not lines[j].lstrip().lower().startswith('end'):
                    j += 1
                    di = self.wrap_procedure(file, procedure, lines, i, j)
                    print('                wrapped', end='')
                    i += di
            print()

        return i


    def save_file(self, file, lines):
        with open(f"{self.SOURCE_DIR}/{file}", 'w') as f:
            for line in lines:
                f.write(line)    


    def modify_stops(self):
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self.SOURCE_DIR):
            files += [os.path.join(dirpath, file).replace(self.SOURCE_DIR,'') for file in filenames]
        files = set([file for file in files if file.endswith('.f') or file.endswith('.f90')])

        for file in files:
            lines = []
            with open(f"{self.SOURCE_DIR}/{file}", 'r') as f:
                lines = f.readlines()

            for i,line in enumerate(lines):
                line = line.lower()
                if line.lstrip().startswith('stop'):

                    lines[i] = line.replace(line[line.index('stop'):], 'return\n')

                    while lines[i].strip().endswith('&') or \
                        lines[i+1].strip().startswith('$') or lines[i+1].strip().startswith('&'):
                        lines[i+1] = ''
                        i += 1

            self.save_file(file, lines)

                        

    def modify_ends(self, lines, procedures):
        for i, line in enumerate(lines):
            if 'end subroutine' in line.lower() or 'end function' in line.lower():
                words = line.strip().split()
                if len(words) == 3:
                    name = line.strip().split()[2]
                    for procedure in procedures:
                        if procedure.name.lower() == name.lower():
                            lines[i] = line.replace(name, f"{get_prefix()}{name}")


    def wrap_procedure(self, lines, procedure):
        prepare_file(f"{self.SOURCE_DIR}/{procedure.file}")
        i = 0

        while not (self.is_procedure_start(lines[i]) and \
              procedure.name == self.get_procedure_name_from_line(lines[i])):
            i += 1
        
        lines[i] = lines[i].replace(procedure.name, f"{get_prefix()}{procedure.name}")
        line = lines[i]

        ind = line.find('(')
        if ind > 0:
            line1 = line[:ind]
            line2 = line[ind:]
            lines[i] = line1
            lines.insert(i+1, line2)

            if procedure.file.strip().endswith('.f'):
                lines[i] = f"{lines[i]}\n"
                lines[i+1] = f"     ${lines[i+1]}"
            if procedure.file.strip().endswith('.f90'):
                lines[i] = f"{lines[i]}&\n"
        
        j = i + 1
        # if procedure.kind == 'function' and not 'result' in procedure.signature:
        #     while not any_in(['return', 'end function'], lines[j]):
        #         lines[j] = lines[j].replace(procedure.name, f"{get_prefix()}{procedure.name}")
        #         j += 1


        # splitted_line = line.split('(')
        # if len(splitted_line) > 1:
        #     lines[i] = splitted_line[0]
        #     lines.insert(i+1, f"({splitted_line[1]}")

        #     if procedure.file.strip().endswith('.f'):
        #         lines[i] = f"{lines[i]}\n"
        #         lines[i+1] = f"     ${lines[i+1]}"
        #     if procedure.file.strip().endswith('.f90'):
        #         lines[i] = f"{lines[i]}&\n"
        

        # if procedure.kind == 'function':
        #     i0 = i
        #     is_result_statement = False
        #     while not lines[i].strip().lower() == procedure.declarations_lines[0].strip().lower():
        #         if 'result' in lines[i].strip().lower():
        #             is_result_statement = True
        #             break
        #         i += 1
        #     print(procedure.name, is_result_statement)

        #procedure.declarations = self.get_declarations(lines,i,procedure)
        wrapper = self.prepare_procedure_wrapper(procedure).split('\n')
        wrapper = [w+'\n' for w in wrapper]
        lines[i:i] = wrapper

        #print(lines[i])

    def find_procedures(self, file, lines):
        procedures = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if self.should_wrap(file, lines, i):
                kind = self.get_procedure_kind_from_line(line)
                if kind == 'subroutine' or kind == 'function':
                    name = self.get_procedure_name_from_line(line)

                    signature_lines = []
                    signature_lines.append(line)
                    signature = name + line[line.find('('):].replace('&', '').strip()
                    while not signature.endswith(')'):
                        i += 1
                        signature += f"{lines[i].replace('&', '').replace('$','').strip()}"
                        signature_lines.append(lines[i])
                    signature_lines = ''.join(signature_lines)

                    # args = []
                    # args_str = signature.replace(name,'') \
                    #     .replace('(', '') \
                    #     .replace(')', '') \
                    #     .replace('&', '') \
                    #     .replace(' ', '')
                    # args = args_str.split(',')    

                    i += 1
                    declarations_lines = []
                    key_words = get_declaration_key_words()
                    end_of_declarations = False
                    while is_declaration(file,lines,i):
                        if not is_comment(file, lines[i]):    
                            declarations_lines.append(lines[i])
                        i += 1

                    # if kind == 'function':
                    #     result_type = self.get_result_type_from_line(line)
                    #     if not result_type:
                    #         result_name = ''
                    #         if 'result' in signature_lines.lower():
                    #             result_search = re.search('result(.*)', signature_lines, re.IGNORECASE)
                    #             if result_search:
                    #                 result_name = result_search.group(1)[1:-1]
                    #         else:
                    #             result_name = name

                    #         for j,dline in enumerate(declarations_lines):
                    #             #if 'implicit' in dline.lower():
                    #             if result_name in dline:
                    #                 declarations_lines[j] = f"{dline.rstrip()}, {get_prefix()}{name}\n"
                    #                 break

                    declarations_lines = ''.join(declarations_lines)
                    procedures.append(self.Procedure(file,kind,name,signature,signature_lines,declarations_lines))

            i += 1
        return procedures


    def wrap(self):
        files = self.prepare_file_list()

        for file in files:
            lines = []
            with open(f"{self.SOURCE_DIR}/{file}", 'r') as f:
                lines = f.readlines()

            procedures = self.find_procedures(file, lines)
            for procedure in procedures:
                print(procedure, end='')
                self.wrap_procedure(lines, procedure)
                print('wrapped')

            self.modify_ends(lines, procedures)

            self.save_file(file,lines)

        self.modify_stops()


