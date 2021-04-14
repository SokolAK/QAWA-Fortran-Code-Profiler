import sys, os
from subroutine_wrapper import Subroutine_wrapper
from function_wrapper import Function_wrapper
from main_wrapper import Main_wrapper
from report import Report_generator
from strings import get_banner
from utils import *
from test_wrappers import Test_wrappers
from config import *
print(get_banner())

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))+'/'

def help():
    print("[QAWA] Help")
    print()
    print(f"Usage: run shell script './qawa <command>' or python script 'python qawa.py <command>'")
    print()
    print(f"List of commands:")
    print(f"wrap [out] ...... add profiling wrappers to files listed in qawa.py.")
    print(f"                  Profiling data will be saved to [out] file located in <QAWA_DIR>/outs/.")
    print(f"                  If no [out] is passed, the output filename is set to 'qawa.out'.")
    #print(f"make -j [N] ............ build wrapped project with N jobs (8 by default)")
    #print(f"build -o [out] -j [N] .. wrap [out] + make with N jobs (8 by default)")
    print(f"unwrap .......... remove profiling wrappers from all files in SOURCE_DIR specified in qawa.py")
    #print(f"restore -j [N].......... unwrap + make with N jobs (8 by default)")
    print(f"report <out> .... generate reports based on the given <out> file")
    print()

def wrong_usage():
    #print("\n[QAWA] *** ERROR: Wrong usage! See the instruction below *** \n")
    help()
    #print("[QAWA] Done")
    sys.exit()

# def find_flag_value(symbol, default):
#     try:
#         id = sys.argv.index(symbol)
#     except:
#         return default
#     try:
#         return type(default)(sys.argv[id+1])
#     except:
#         wrong_usage()

def wrap():
    #OUT_FILE = find_flag_value('-o', 'qawa.out')
    OUT_FILE = sys.argv[2] if len(sys.argv) > 2 else 'qawa.out'
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
    print("[QAWA] Unwrapping...")
    unwrap_dir(SOURCE_DIR)

# def rewrap():
#     unwrap()
#     wrap()

# def make(N=8, clean=False):
#     print("[QAWA] Building executable...")
#     N = find_flag_value('-j', 8)
#     os.chdir(os.path.dirname(MAKEFILE))
#     if clean:
#         os.system("make clean")
#     os.system(f"make -j {N}")

# def build():
#     wrap()
#     make()

# def rebuild():
#     unwrap()
#     build()

# def restore():
#     unwrap()
#     make(clean=True)

def report():
    if len(sys.argv) < 3:
        wrong_usage()

    print("[QAWA] Generating reports...")
    report_generator = Report_generator(sys.argv[2])
    report_generator.generate_report()

def test():
    print("[QAWA] Testing...")
    os.system('python test_wrappers.py')


if len(sys.argv) < 2:
    wrong_usage()

commands = {
    'help': help,
    'wrap': wrap,
    'unwrap': unwrap,
    #'build': build,
    #'make': make,
    #'rebuild': rebuild,
    #'restore': restore,
    'report': report,
    'test': test,
    #'rewrap': rewrap
}
command = sys.argv[1]
function = commands.get(command,help)

if not os.path.exists(f"{SCRIPT_DIR}outs"):
    os.makedirs(f"{SCRIPT_DIR}outs")

function()
print("[QAWA] Done")
