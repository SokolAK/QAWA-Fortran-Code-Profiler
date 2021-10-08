import os


def prepare_file_list(SOURCE_DIR, FILES):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(SOURCE_DIR):
        files += [os.path.join(dirpath, file).replace(SOURCE_DIR,'') for file in filenames]
    files = set([file for file in files if file.endswith('.f') or file.endswith('.f90')])
    files = [f for f in files if f in FILES or '*' in FILES]
    files = [f for f in files if f"-{f}" not in FILES]
    files = [f"{SOURCE_DIR}{f}" for f in files]
    return files


def read_file(filename):
    lines = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    return lines