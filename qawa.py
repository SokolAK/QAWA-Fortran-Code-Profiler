import sys, os
from qawa_subroutine_wrapper import Subroutine_wrapper
from qawa_function_wrapper import Function_wrapper
from qawa_main_wrapper import Main_wrapper
from qawa_report import Report_generator
from qawa_strings import get_banner
from qawa_utils import *
print(get_banner())

# USER SETTINGS
########################################################################
PROJECT_DIR = '/home/adam.sokol/QCHEM/GAMMCOR_GitLab/'
MAKEFILE = PROJECT_DIR + 'Makefile'
SOURCE_DIR = PROJECT_DIR + 'SOURCE/'
MAIN_FILE = SOURCE_DIR + 'mainp.f'
SUBROUTINES_FILES = ['*', '-sorter.f90', '-tran.f90', '-timing.f90']
SUBROUTINES = ['*', '-ints_modify']
FUNCTIONS_FILES = ['*', '-timing.f90', '-types.f90', '-interpa.f']
FUNCTIONS = ['*']
########################################################################
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def help():
    print("[QAWA] Help")
    print()
    print(f"""Usage: qawa <command>\n
List of commands:
    wrap [out]    --  add profiling wrappers to files listed in qawa.py. 
                      Profiling data will be saved to [out] file located in <QAWA_DIR>/outs/.
                      If no [out] is passed, the output filename is set to 'qawa.out'.
    make          --  build wrapped project
    build [out]   --  wrap [out] + make
    unwrap        --  remove profiling wrappers from all files in SOURCE_DIR specified in qawa.py
    restore       --  unwrap + make
    report <out>  --  generate reports based on the given <out> file
    """)

def wrong_usage():
    help()
    print("[QAWA] Done")
    exit()

def wrap():
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

def rewrap():
    unwrap()
    wrap()

def make(clean=False):
    print("[QAWA] Building executable...")
    os.chdir(os.path.dirname(MAKEFILE))
    if clean:
        os.system("make clean")
    os.system("make -j 4")

def build():
    wrap()
    make()

def rebuild():
    unwrap()
    build()

def restore():
    unwrap()
    make(clean=True)

def generate_report():
    if len(sys.argv) < 3:
        wrong_usage()

    print("[QAWA] Generating reports...")
    report_generator = Report_generator(sys.argv[2])
    report_generator.generate_report()


if len(sys.argv) < 2:
    wrong_usage()

commands = {
    'help': help,
    'wrap': wrap,
    'unwrap': unwrap,
    'build': build,
    'make': make,
    #'rebuild': rebuild,
    'restore': restore,
    'report': generate_report
    #'rewrap': rewrap
}
command = sys.argv[1]
function = commands.get(command,help)
function()
print("[QAWA] Done")


