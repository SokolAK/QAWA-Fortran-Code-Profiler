import sys, os
from subroutine_def_wrapper import Subroutine_def_wrapper
from subroutine_call_wrapper import Subroutine_call_wrapper
from function_wrapper import Function_wrapper
from main_wrapper import Main_wrapper
from report_generator import * 
from flow_generator import * 
from chain_generator import *
from mem_generator import *
from comparison_generator import *
from strings import get_banner
from utils import *
from shutil import copy
from test_wrappers import Test_wrappers

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))+'/'
SOURCE_DIR = MAIN_FILE = ''
SUBROUTINES_FILES = SUBROUTINES = FUNCTIONS_FILES = FUNCTIONS = []
SUBROUTINE_METHOD = ''
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

def violet(text):
    return f"{COLORS['violet']}{text}{COLORS['normal']}"
def cyan(text):
    return f"{COLORS['cyan']}{text}{COLORS['normal']}"
def yellow(text):
    return f"{COLORS['yellow']}{text}{COLORS['normal']}"
def red(text):
    return f"{COLORS['red']}{text}{COLORS['normal']}"
def green(text):
    return f"{COLORS['green']}{text}{COLORS['normal']}"
def bold(text):
    return f"{COLORS['bold']}{text}{COLORS['normal']}"
def underline(text):
    return f"{COLORS['underline']}{text}{COLORS['normal']}"

def help():
    print(f"{bold('[QAWA FCP] Help')}")
    print()
    print(f"{bold('Usage:')} run shell script {cyan('./qawa <command>')} or python script python {cyan('qawa.py <command>')}")
    print(f"{bold('Examples:')} {cyan('./qawa wrap filename1.py -o filename2')} or {cyan('python qawa.py unwrap filename1.py')}")
    print()
    print(f"{bold(underline('List of commands:'))}")
    print(f"({red('<value>')} is required, {yellow('-flag [value]')} is optional)")
    print()
    
    print(f"""{cyan('wrap')} {red('<config.py>')} {yellow('-o [file]')}
    Add TIME profiling wrappers to files listed in <config.py>.")
    Profiling data will be saved to [file].out file located in <QAWA_DIR>/outs/.")
    If no [out] is passed, the output filename is set to 'qawa.out'.""")

    print(f"""{cyan('report')} {red('<out>')}
    Generate TIME reports based on the given <out> file.""")
    print(f"""{cyan('compare')} {red('<out1> <out2> ...')}
    Generate TIME reports and compare reports for the given out files.""")
    print(f"""{cyan('unwrap')} {red('<config.py>')}
    Restore the original version of the source files listed in <config.py>)
    from before the wrapping process.""")
    print()


def wrong_usage():
    help()
    sys.exit()


def find_flag_value(symbol, default):
    try:
        id = sys.argv.index(symbol)
    except:
        return default
    try:
        return type(default)(sys.argv[id+1])
    except:
        wrong_usage()


def prepare_config():
    if len(sys.argv) < 3:
        wrong_usage()
    else:
        if os.path.isfile(sys.argv[2]):
            config_temp_path = f"{SCRIPT_DIR}/config_temp.py"
            copy(sys.argv[2], config_temp_path)
        else:
            #raise Exception(f"Config file '{sys.argv[2]}' not found!")
            print(f"Config file '{sys.argv[2]}' not found!")
            sys.exit()

    import config_temp
    global SOURCE_DIR, MAIN_FILE, SUBROUTINES_FILES, SUBROUTINES, FUNCTIONS_FILES, FUNCTIONS, SUBROUTINE_METHOD
    SOURCE_DIR = config_temp.SOURCE_DIR
    MAIN_FILE = config_temp.MAIN_FILE
    SUBROUTINES_FILES = config_temp.SUBROUTINES_FILES
    SUBROUTINES = config_temp.SUBROUTINES
    SUBROUTINE_METHOD = config_temp.SUBROUTINE_WRAPPING_METHOD
    FUNCTIONS_FILES = config_temp.FUNCTIONS_FILES
    FUNCTIONS = config_temp.FUNCTIONS
    
    if os.path.isfile(config_temp_path):
        os.remove(config_temp_path)


def wrap():
    #OUT_FILE = sys.argv[2] if len(sys.argv) > 2 else 'qawa.out'
    OUT_FILE = find_flag_value('-o', 'qawa.out')
    unwrap()

    print("[QAWA] Wrapping main...")
    main_wrapper = Main_wrapper(SCRIPT_DIR, MAIN_FILE, OUT_FILE)
    main_wrapper.wrap()

    print("[QAWA] Wrapping subroutines...")
    sub_wrapper = Subroutine_def_wrapper(SCRIPT_DIR=SCRIPT_DIR, 
        SOURCE_DIR=SOURCE_DIR,
        OUT_FILE=OUT_FILE,
        FILES=SUBROUTINES_FILES,
        SUBROUTINES=SUBROUTINES)
    if SUBROUTINE_METHOD == 'call':
        sub_wrapper = Subroutine_call_wrapper(SCRIPT_DIR=SCRIPT_DIR, 
            SOURCE_DIR=SOURCE_DIR,
            OUT_FILE=OUT_FILE,
            FILES=SUBROUTINES_FILES,
            SUBROUTINES=SUBROUTINES,
            MAIN_FILE=MAIN_FILE)
    sub_wrapper.wrap()
    
    print("[QAWA] Wrapping functions...")
    fun_wrapper = Function_wrapper(SCRIPT_DIR=SCRIPT_DIR, 
        SOURCE_DIR=SOURCE_DIR,
        OUT_FILE=OUT_FILE,
        FILES=FUNCTIONS_FILES,
        FUNCTIONS=FUNCTIONS)
    fun_wrapper.wrap()

    # print("[QAWA] Generating wrap report...")
    # generate_wrap_report(SCRIPT_DIR, SOURCE_DIR, \
    #                      SUBROUTINES_FILES, FUNCTIONS_FILES, \
    #                      SUBROUTINES, FUNCTIONS, MAIN_FILE,
    #                      SUBROUTINE_METHOD)

def unwrap():
    prepare_config()
    if len(sys.argv) < 3:
        wrong_usage()
    else:
        print("[QAWA] Unwrapping...")
        unwrap_dir(SOURCE_DIR)


def report():
    if len(sys.argv) < 3:
        wrong_usage()
    print("[QAWA] Generating reports...")
    Report_generator(sys.argv[2]).generate_report()


def report_mt(filename=''):

    if not filename:
        if len(sys.argv) < 3:
            wrong_usage()
        print("[QAWA] Generating reports...")
        filename = sys.argv[2]

    if is_new_report_format(filename):
        covnert_report_to_old_format(filename)

    Flow_generator(filename).generate_report()
    Chain_generator(filename).generate_report()
    Mem_generator(f"{filename[:-4]}-mem.out").generate_report()


def compare():
    if len(sys.argv) < 3:
        wrong_usage()
    print("[QAWA] Generating reports...")
    
    for filename in sys.argv[2:]:
        report_mt(filename)

    Comparison_generator(sys.argv[2:]).generate_report()


def test():
    print("[QAWA] Testing...")
    os.system('python test_wrappers.py')


########################################################################
print(f"{violet(get_banner())}")

if len(sys.argv) < 2:
    wrong_usage()

commands = {
    'help': help,
    'wrap': wrap,
    'unwrap': unwrap,
    'report': report_mt,
    'report_old': report,
    'compare': compare,
    'test': test,
}
command = sys.argv[1]
function = commands.get(command,help)

if not os.path.exists(f"{SCRIPT_DIR}outs"):
    os.makedirs(f"{SCRIPT_DIR}outs")

function()
print("[QAWA] Done")
