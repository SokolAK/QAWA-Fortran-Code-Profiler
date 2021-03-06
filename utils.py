import os
from shutil import copy
from strings import get_prefix
from line_utils import is_comment, get_procedure_name_from_line, \
                is_enter, is_exit, unpack_enter_line, unpack_exit_line

def convert_text_block_from_f77_to_f90(text_block):
    text_lines = [line.lstrip() for line in text_block.split('\n')]
    for i, line in enumerate(text_lines):
        line = line.lstrip() 
        if line.startswith('$') or line.startswith('&'):
            text_lines[i] = line.replace('$','&')
            #text_lines[i] = line[1:]
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
    print(f"FILES: {files}")
    return files

    
def is_f90_format(file):
    return file.lower().rstrip().endswith('.f90')


def save_file(file, lines, header=[], mode='w'):
    with open(file, mode) as f:
        for line in header:
            f.write(line)
        for line in lines:
            f.write(line)  


def read_file(filename, strip=False):
    lines = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    if strip:
        for i in range(len(lines)):
            lines[i] = lines[i].strip()
    return lines


def get_threads_nums(lines):
    threads_nums = set()
    for line in lines:
        threads_nums.add(int(line.split()[4]))
    threads_nums = sorted(threads_nums)
    return threads_nums


def get_substring_symbol(string, symbol, order, dire):
    i = 0
    if order == 'first':
        i = string.find(symbol)
    if order == 'last':
        i = string.rfind(symbol)

    if i < 0:
        return string

    if dire == 'left':
        return string[:i].rstrip()
    if dire == 'right':
        return string[i+1:].lstrip()

    return ''


def generate_wrap_report(SCRIPT_DIR, SOURCE_DIR, SUBROUTINES_FILES, \
                        FUNCTIONS_FILES, SUBROUTINES, FUNCTIONS, \
                        MAIN_FILE, SUBROUTINE_METHOD):

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

        lines = read_file(f"{MAIN_FILE}")
        wrapped = ''
        error = ''
        open_clause = False
        close_clause = False
        for line in lines:
            if f"open_{get_prefix()}main" in line:
                open_clause = True
            if f"close_{get_prefix()}main" in line:
                close_clause = True
        if open_clause and close_clause:
            wrapped = 'wrapped'
        else:
            error = 'error'

        f.write(f"{MAIN_FILE.split('/')[-1]:30s}{'MAIN':30s}{'M':10s}{wrapped:20s}{error:20s}\n")


def prepare_paths(lines, max_thds):
    paths = []
    for i in range(max_thds):
        paths.append([])

    for line in lines:
        if is_enter(line):
            dire, file, name, typ, thread, max_threads = unpack_enter_line(line)
        if is_exit(line):
            dire, file, name, typ, thread, max_threads, stime, ctime, wtime = unpack_exit_line(line)

        if thread == 1 and max_threads == 1:
            for path in paths:
                path.append(line)
        else:
            paths[thread-1].append(line)

    return paths


def is_new_report_format(filename):
    with open(filename, 'r') as f:
        firstLine = f.readline()
    return firstLine and is_enter(firstLine) and len(firstLine.split()) == 9


def covnert_report_to_old_format(filename):
    store = {}
    lines = read_file(filename)

    with open(filename, 'w') as f:

        for line in lines:

            proc_name = f"{line.split()[1]}{line.split()[2]}"
            wtime = float(line.split()[6])
            ctime = float(line.split()[7])
            wtime_q = float(line.split()[8])

            if is_enter(line):
                store[proc_name] = [wtime,ctime,wtime_q]
                for i in range(6):
                    f.write(f"{line.split()[i]} ")
                f.write("\n")

            if is_exit(line):
                [wtime0,ctime0,wtime_q0] = store[proc_name]
                del store[proc_name]

                for i in range(6):
                    f.write(f"{line.split()[i]} ")
                f.write(f"{wtime-wtime0} ")
                f.write(f"{ctime-ctime0} ")
                f.write(f"{wtime_q-wtime_q0}")
                f.write("\n")
    