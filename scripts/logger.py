COLORS = {
    'violet': '\033[95m',
    'blue': '\033[94m',
    'cyan': '\033[96m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'red': '\033[91m',
    'normal': '\033[0m',
    'bold': '\033[1m',
    'underline': '\033[4m'
}

LEVELS = {
    '' : 'normal',
    'info': 'cyan',
    'warning': 'yellow',
    'error': 'red',
    'success': 'green',
    'detail': 'normal'
    }


def colorize(text, color):
    return f"{COLORS[color]}{text}{COLORS['normal']}"


def violet(text):
    return colorize(text, 'violet')
def cyan(text):
    return colorize(text, 'cyan')
def yellow(text):
    return colorize(text, 'yellow')
def red(text):
    return colorize(text, 'red')
def green(text):
    return colorize(text, 'green')
def bold(text):
    return colorize(text, 'bold')
def underline(text):
    return colorize(text, 'underline')


def log(text, level='', source=''):
    color = LEVELS[level.lower()]
    level = f'[{level.upper()}] ' if level else ''
    source = f'({source}) ' if source else ''
    print( colorize(level + source + text, color) )


