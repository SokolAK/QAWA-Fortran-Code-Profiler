def is_enter(line):
    return line.startswith('->')


def is_exit(line):
    return line.startswith('<-')


def unpack_line(line):
        line = line.rstrip()
        if is_enter(line):
            dire, file, name, typ, thread, max_threads = unpack_enter_line(line)
            return dire, file, name, typ, thread, max_threads, 0, 0, 0
        if is_exit(line):
            return unpack_exit_line(line)  


def unpack_enter_line(line):
    dire, file, name, typ, thread, max_threads = line.split()
    return dire, file, name, typ, int(thread), int(max_threads)


def unpack_exit_line(line):
    dire, file, name, typ, thread, max_threads, stime, ctime, wtime = line.split()
    return dire, file, name, typ, int(thread), int(max_threads), float(stime), float(ctime), float(wtime)


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