import sys, os
from subroutine_wrapper import Subroutine_wrapper
from function_wrapper import Function_wrapper
from main_wrapper import Main_wrapper
from report import Report_generator
from strings import get_banner
from utils import *
from shutil import copy
from test_wrappers import Test_wrappers
print(get_banner())

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))+'/'
SOURCE_DIR = MAIN_FILE = ''
SUBROUTINES_FILES = SUBROUTINES = FUNCTIONS_FILES = FUNCTIONS = []

def help():
    print("[QAWA] Help")
    print()
    print(f"Usage: run shell script './qawa <command>' or python script 'python qawa.py <command>'")
    print()
    print(f"List of commands:")
    print(f"wrap <config.py> -o [out] .... Add profiling wrappers to files listed in <config.py>.")
    print(f"                               Profiling data will be saved to [out] file located in <QAWA_DIR>/outs/.")
    print(f"                               If no [out] is passed, the output filename is set to 'qawa.out'.")
    print(f"unwrap <config.py> ........... Restore the original version of the source files listed in <config.py>")
    print(f"                               from before the wrapping process.")
    print(f"report <out> ................. Generate reports based on the given <out> file.")
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
    global SOURCE_DIR, MAIN_FILE, SUBROUTINES_FILES, SUBROUTINES, FUNCTIONS_FILES, FUNCTIONS
    SOURCE_DIR = config_temp.SOURCE_DIR
    MAIN_FILE = config_temp.MAIN_FILE
    SUBROUTINES_FILES = config_temp.SUBROUTINES_FILES
    SUBROUTINES = config_temp.SUBROUTINES
    FUNCTIONS_FILES = config_temp.FUNCTIONS_FILES
    FUNCTIONS = config_temp.FUNCTIONS
    
    if os.path.isfile(config_temp_path):
        os.remove(config_temp_path)


def wrap():
    #OUT_FILE = sys.argv[2] if len(sys.argv) > 2 else 'qawa.out'
    OUT_FILE = find_flag_value('-o', 'qawa.out')
    unwrap()

    print("[QAWA] Wrapping subroutines...")
    sub_wrapper = Subroutine_wrapper(SCRIPT_DIR=SCRIPT_DIR, 
        SOURCE_DIR=SOURCE_DIR,
        OUT_FILE=OUT_FILE,
        FILES=SUBROUTINES_FILES,
        SUBROUTINES=SUBROUTINES)
    sub_wrapper.wrap()
    
    print("[QAWA] Wrapping functions...")
    fun_wrapper = Function_wrapper(SCRIPT_DIR=SCRIPT_DIR, 
        SOURCE_DIR=SOURCE_DIR,
        OUT_FILE=OUT_FILE,
        FILES=FUNCTIONS_FILES,
        FUNCTIONS=FUNCTIONS)
    fun_wrapper.wrap()

    print("[QAWA] Wrapping main...")
    main_wrapper = Main_wrapper(SCRIPT_DIR, MAIN_FILE, OUT_FILE)
    main_wrapper.wrap()

    print("[QAWA] Generating wrap report...")
    generate_wrap_report(SCRIPT_DIR, SOURCE_DIR, SUBROUTINES_FILES, FUNCTIONS_FILES, SUBROUTINES, FUNCTIONS)


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
    report_generator = Report_generator(sys.argv[2])
    report_generator.generate_report()


def test():
    print("[QAWA] Testing...")
    os.system('python test_wrappers.py')


########################################################################
if len(sys.argv) < 2:
    wrong_usage()

commands = {
    'help': help,
    'wrap': wrap,
    'unwrap': unwrap,
    'report': report,
    'test': test,
}
command = sys.argv[1]
function = commands.get(command,help)

if not os.path.exists(f"{SCRIPT_DIR}outs"):
    os.makedirs(f"{SCRIPT_DIR}outs")

function()
print("[QAWA] Done")
