import sys, os
from shutil import copy, move
from scripts.logger import log

FILENAME = os.path.basename(__file__)

def prepare_configuration():

    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))+'/'
    
    if os.path.isfile(sys.argv[2]):
        config_temp_path = f"{CURRENT_DIR}/config_temp.py"
        copy(sys.argv[2], config_temp_path)
    else:
        #raise Exception(f"Config file '{sys.argv[2]}' not found!")
        print(f"Config file '{sys.argv[2]}' not found!")
        sys.exit()

    from scripts import config_temp

    if os.path.isfile(config_temp_path):
        os.remove(config_temp_path)

    return  {
        # 'COMPILER': config_temp.COMPILER,
        # 'COMPILER_OPTIONS': config_temp.COMPILER_OPTIONS,
        'SOURCE_DIR': config_temp.SOURCE_DIR,
        'MAIN_FILE': config_temp.MAIN_FILE,
        'SUBROUTINES_FILES': config_temp.SUBROUTINES_FILES,
        'SUBROUTINES': config_temp.SUBROUTINES,
        'FUNCTIONS_FILES': config_temp.FUNCTIONS_FILES,
        'FUNCTIONS': config_temp.FUNCTIONS
        }


def create_module(CONFIGURATION):
    pass
    # log('Compiling dictionary_m', level='info', source=FILENAME)
    # os.system(f"{CONFIGURATION['COMPILER']} {CONFIGURATION['COMPILER_OPTIONS']} -c ./source/qawa_dictionary_m.f90")

    # log('Compiling qawa_procedures', level='info', source=FILENAME)
    # os.system(f"{CONFIGURATION['COMPILER']} {CONFIGURATION['COMPILER_OPTIONS']} -c ./source/qawa_procedures_m.f90")

    # log('Copying files', level='info', source=FILENAME)
    # copy('qawa_procedures_m.mod', CONFIGURATION['SOURCE_DIR'])
    # copy('qawa_dictionary_m.mod', CONFIGURATION['SOURCE_DIR'])

    # log('Cleaning', level='info', source=FILENAME)
    # os.remove('qawa_procedures_m.mod')
    # os.remove('qawa_procedures_m.o')
    # os.remove('qawa_dictionary_m.mod')
    # os.remove('qawa_dictionary_m.o')