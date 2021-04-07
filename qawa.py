import sys, os
from qawa_subroutine_wrapper import Subroutine_wrapper
from qawa_main_wrapper import Main_wrapper
from qawa_report import Report_generator
from qawa_strings import print_banner
from qawa_utils import *
print_banner()

# USER SETTINGS
########################################################################
PROJECT_DIR = '/home/adam.sokol/QCHEM/GAMMCOR_GitLab/'
MAKEFILE = PROJECT_DIR + 'Makefile'
SOURCE_DIR = PROJECT_DIR + 'SOURCE/'
MAIN_FILE = SOURCE_DIR + 'mainp.f'
FILES = ['*', '-sorter.f90', '-tran.f90', '-timing.f90']
#FILES = ['misc.f']
SUBROUTINES = ['*', '-ints_modify']
FUNCTIONS = []
########################################################################

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def help():
    print("[QAWA] Help")
    print(f"""Usage: qawa <command>
List of commands:
    wrap            -- add profiling wrappers to files listed in qawa.py
    make            -- rebuild wrapped project
    build           -- wrap + make
    unwrap          -- remove profiling wrappers from all files in SOURCE_DIR (qawa.py)
    restore         -- unwrap + make
    rebuild         -- unwrap + wrap + make
    report <out>    -- generate reports based on the given <out> file
    """)

def wrap():
    print("[QAWA] Wrapping...")
    sub_wrapper = Subroutine_wrapper(SCRIPT_DIR=SCRIPT_DIR, 
        SOURCE_DIR=SOURCE_DIR,
        FILES=FILES,
        SUBROUTINES=SUBROUTINES)
    sub_wrapper.wrap()

    main_wrapper = Main_wrapper(SCRIPT_DIR, MAIN_FILE)
    main_wrapper.wrap()


def unwrap():
    print("[QAWA] Unwrapping...")
    unwrap_dir(SOURCE_DIR)

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
        help()
    else:
        print("[QAWA] Generating report...")
        report_generator = Report_generator(sys.argv[2])
        report_generator.generate_report()


if len(sys.argv) < 2:
    help()
else:
    commands = {
        'help': help,
        'wrap': wrap,
        'unwrap': unwrap,
        'build': build,
        'make': make,
        'rebuild': rebuild,
        'restore': restore,
        'report': generate_report
    }
    command = sys.argv[1]
    function = commands.get(command,help)
    function()
    print("[QAWA] Done")


