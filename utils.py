import os
from shutil import copy
from strings import get_prefix


def get_declaration_key_words():
    return ['program','use','include','data','implicit','external', \
            'character','real','double','integer','dimension','logical', \
            'complex','parameter','type','common']


def is_broken_line(lines, i):
    return lines[i].rstrip().endswith('&') or lines[i+1].lstrip().startswith('&') or lines[i+1].lstrip().startswith('$')

def is_comment(file, line):
    if not line.strip():
        return True

    if file.strip().endswith('.f'):
        first_char = line.lower()[0]
        return first_char == 'c' or first_char == 'd' or first_char == '*' or first_char == '!'

    if file.strip().endswith('.f90'):
        first_char = line.strip().lower()[0]
        return first_char == '!'

    return False


def is_declaration(file, lines, i):
    for key_word in get_declaration_key_words():
        if lines[i].strip().lower().startswith(key_word) or \
                not lines[i].strip() or \
                is_comment(file, lines[i]) or \
                lines[i].strip().startswith('$') or \
                lines[i].strip().startswith('&') or \
                lines[i-1].strip().endswith('&'):

            return True
    return False


def convert_text_block_from_f77_to_f90(text_block):
    text_lines = [line.lstrip() for line in text_block.split('\n')]
    for i, line in enumerate(text_lines):
        line = line.lstrip() 
        if line.startswith('$') or line.startswith('&'):
            text_lines[i] = line[1:]
            text_lines[i-1] = f"{text_lines[i-1]}&"

    text_block = '\n'.join(text_lines)
    return text_block


def does_file_exist(filename):
    return os.path.isfile(filename)


def make_copy(org_name):
    copy_name = f"{org_name}.qawa_copy"
    if not does_file_exist(copy_name):
        copy(org_name, copy_name)


def unwrap_file(copy_name):
    org_name = copy_name.replace('.qawa_copy', '')
    if os.path.isfile(org_name):
        os.remove(org_name)
    if os.path.isfile(copy_name):
        os.rename(copy_name, org_name)


def unwrap_dir(SOURCE_DIR):
	files = []
	for (dirpath, dirnames, filenames) in os.walk(SOURCE_DIR):
		files += [os.path.join(dirpath, file).replace(SOURCE_DIR,'') for file in filenames]
	files = set([file for file in files if '.qawa_copy' in file])
	print(f"Restoring: {files}")
	for file_copy in files:
		unwrap_file(f"{SOURCE_DIR}{file_copy}")


def prepare_file(filename):
    copy_name = f"{filename}.qawa_copy"
    if does_file_exist(copy_name):
        unwrap_file(copy_name)
    make_copy(filename)


def get_separator(symbol, length):
    return ''.join([symbol]*length)

def any_in(key_words, line):
    line = line.strip().lower()
    for key_word in key_words:
        if key_word in line:
            return True
    return False

def prepare_file_list(SOURCE_DIR, FILES):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(SOURCE_DIR):
        files += [os.path.join(dirpath, file).replace(SOURCE_DIR,'') for file in filenames]
    files = set([file for file in files if file.endswith('.f') or file.endswith('.f90')])
    #files.update([f for f in listdir(SOURCE_DIR) if isfile(join(SOURCE_DIR, f))])
    files = [f for f in files if f in FILES or '*' in FILES]
    files = [f for f in files if f"-{f}" not in FILES]
    #print(f"FILES: {files}")
    return files

def get_procedure_name_from_line(line):
    i = 0
    if 'subroutine' in line.lower():
        i = line.lower().find('subroutine') + 10
    if 'function' in line.lower():
        i = line.lower().find('function') + 8
    tab = len(line[i:]) - len(line[i:].lstrip())
    i += tab
    line = line[i:].rstrip()

    if line.endswith('&'):
        line = line[:-1].rstrip()

    iE = line.find('(')
    return line[:iE] if iE > 0 else line
    
def is_f90_format(file):
    return file.lower().rstrip().endswith('.f90')


def save_file(file, lines):
    with open(file, 'w') as f:
        for line in lines:
            f.write(line)  

def read_file(filename):
    lines = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    return lines


def generate_wrap_report(SCRIPT_DIR, SOURCE_DIR, SUBROUTINES_FILES, FUNCTIONS_FILES, SUBROUTINES, FUNCTIONS):
    with open(f"{SCRIPT_DIR}outs/qawa_wrap_report", 'w') as f:

        files = prepare_file_list(SOURCE_DIR, ['*'])
        for file in files:
            lines = read_file(f"{SOURCE_DIR}{file}")
            for i, line in enumerate(lines):
                typ = '-'
                wrapped = ''
                error = ''
                name = ''

                if not is_comment(file, line) and not get_prefix() in line:
                    if line.lower().strip().startswith('subroutine'):
                        typ = 'S'
                        name = get_procedure_name_from_line(line)
                        for j in range(i+1, len(lines), 1):
                            if f"{get_prefix()}{name}" in lines[j]:
                                wrapped = 'wrapped'
                                break
                        if file in SUBROUTINES_FILES or ('*' in SUBROUTINES_FILES and f"-{file}" not in SUBROUTINES_FILES):
                            if name in SUBROUTINES or ('*' in SUBROUTINES and f"-{name}" not in SUBROUTINES):
                                if not wrapped:
                                    error = 'error'

                    if not 'end' in line.lower()+' ' and 'function ' in line.lower():
                        typ = 'F'
                        fragment_open = False
                        fragment_close = False
                        name = get_procedure_name_from_line(line)
                        for j in range(i+1, len(lines), 1):
                            if f"open_{get_prefix()}{name}" in lines[j]:
                                fragment_open = True
                            if f"close_{get_prefix()}{name}" in lines[j]:
                                fragment_close = True
                            if fragment_open and fragment_close:
                                wrapped = 'wrapped'
                                break
                        if file in FUNCTIONS_FILES or ('*' in FUNCTIONS_FILES and f"-{file}" not in FUNCTIONS_FILES):
                            if name in FUNCTIONS or ('*' in FUNCTIONS and f"-{name}" not in FUNCTIONS):
                                if not wrapped:
                                    error = 'error'

                            #if f"{get_prefix()}{get_procedure_name_from_line(line)}" in lines[j]:
                            #    wrapped = 'wrapped'
                            #    break

                    if typ in 'FS':
                        #wrapped_procedures.append([file, get_procedure_name_from_line(line), typ, wrapped, error])
                        f.write(f"{file:30s}{name:30s}{typ:10s}{wrapped:20s}{error:20s}\n")  