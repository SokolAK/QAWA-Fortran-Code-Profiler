import os
from shutil import copy

def get_declaration_key_words():
    return ['program','use','include','data','implicit','character', \
            'real','double','integer','dimension','logical','complex', \
            'parameter','type', 'common']


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
    os.remove(org_name)
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