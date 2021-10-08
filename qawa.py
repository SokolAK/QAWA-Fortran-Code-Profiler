import sys, os
from scripts.flow_generator import * 
from scripts.chain_generator import *
from scripts.comparison_generator import *
from scripts.strings import get_banner
from scripts.initializr import prepare_configuration, create_module
from scripts.logger import *
import scripts.subroutine_wrapper as subroutine_wrapper
import scripts.main_wrapper as main_wrapper


FILENAME = os.path.basename(__file__)
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))+'/'
SOURCE_DIR = MAIN_FILE = ''
SUBROUTINES_FILES = SUBROUTINES = FUNCTIONS_FILES = FUNCTIONS = []

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


def wrap():
    if len(sys.argv) < 3:
        wrong_usage()

    CONFIGURATION = prepare_configuration()
    create_module(CONFIGURATION)

    subroutine_wrapper.run(CONFIGURATION)
    main_wrapper.run(CONFIGURATION)

    #OUT_FILE = sys.argv[2] if len(sys.argv) > 2 else 'qawa.out'
    # OUT_FILE = find_flag_value('-o', 'qawa.out')
    # unwrap()

    # print("[QAWA] Wrapping main...")
    # main_wrapper = Main_wrapper(SCRIPT_DIR, MAIN_FILE, OUT_FILE)
    # main_wrapper.wrap()

    # print("[QAWA] Wrapping subroutines...")
    # sub_wrapper = Subroutine_wrapper(SCRIPT_DIR=SCRIPT_DIR, 
    #     SOURCE_DIR=SOURCE_DIR,
    #     OUT_FILE=OUT_FILE,
    #     FILES=SUBROUTINES_FILES,
    #     SUBROUTINES=SUBROUTINES)
    # sub_wrapper.wrap()
    
    # print("[QAWA] Wrapping functions...")
    # fun_wrapper = Function_wrapper(SCRIPT_DIR=SCRIPT_DIR, 
    #     SOURCE_DIR=SOURCE_DIR,
    #     OUT_FILE=OUT_FILE,
    #     FILES=FUNCTIONS_FILES,
    #     FUNCTIONS=FUNCTIONS)
    # fun_wrapper.wrap()

    # print("[QAWA] Generating wrap report...")
    # generate_wrap_report(SCRIPT_DIR, SOURCE_DIR, \
    #                      SUBROUTINES_FILES, FUNCTIONS_FILES, \
    #                      SUBROUTINES, FUNCTIONS, MAIN_FILE)

def unwrap():
    CONFIGURATION = prepare_configuration()
    if len(sys.argv) < 3:
        wrong_usage()
    else:
        log('Unwrapping', level='info', source=FILENAME)
        unwrap_dir(CONFIGURATION['SOURCE_DIR'])


def report():
    if len(sys.argv) < 3:
        wrong_usage()
    log('Generating reports', level='info', source=FILENAME)
    Report_generator(sys.argv[2]).generate_report()


def report_mt(filename=''):

    if not filename:
        if len(sys.argv) < 3:
            wrong_usage()
        log('Generating reports', level='info', source=FILENAME)
        filename = sys.argv[2]

    Flow_generator(filename).generate_report()
    Chain_generator(filename).generate_report()


def compare():
    if len(sys.argv) < 3:
        wrong_usage()
    log('Generating reports', level='info', source=FILENAME)
    
    for filename in sys.argv[2:]:
        report_mt(filename)

    Comparison_generator(sys.argv[2:]).generate_report()


def test():
    log('Testing', level='info', source=FILENAME)
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
log('Done', level='success', source=FILENAME)
