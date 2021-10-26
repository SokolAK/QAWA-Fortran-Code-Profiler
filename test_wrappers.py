import unittest
import os
from utils import unwrap_file, read_file, does_file_exist
from subroutine_def_wrapper import Subroutine_def_wrapper
from function_wrapper import Function_wrapper
from main_wrapper import Main_wrapper

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = SCRIPT_DIR
MAKEFILE = PROJECT_DIR + ''
SOURCE_DIR = PROJECT_DIR + '/test/'
MAIN_FILE = 'test_main.f'
TEST_DATA_FILE_F90 = 'test_data.f90'
TEST_DATA_FILE_F77 = 'test_data.f'
SUBROUTINES = ['*', '-not_sub1']
FUNCTIONS_FILES = [TEST_DATA_FILE_F90, TEST_DATA_FILE_F77]
FUNCTIONS = ['*', '-not_fun1']
OUT_FILE = 'qawa.out'

def compare(obj, filename):
    wrapped = ''.join(read_file(f"{SOURCE_DIR}{filename}"))
    reference = ''.join(read_file(f"{SOURCE_DIR}ref_{filename}"))
    obj.assertEqual(wrapped, reference)

def test_subroutines(name, file):
    print(f"\n* {name}")
    sub_wrapper = Subroutine_wrapper(SCRIPT_DIR=SCRIPT_DIR, 
        SOURCE_DIR=SOURCE_DIR,
        OUT_FILE=OUT_FILE,
        FILES=[file],
        SUBROUTINES=SUBROUTINES)
    sub_wrapper.wrap()

def test_functions(name, file):
    print(f"\n* {name}")
    fun_wrapper = Function_wrapper(SCRIPT_DIR=SCRIPT_DIR, 
        SOURCE_DIR=SOURCE_DIR,
        OUT_FILE=OUT_FILE,
        FILES=[file],
        FUNCTIONS=FUNCTIONS)
    fun_wrapper.wrap()

def test_main(name, file):
    print(f"\n* {name}")
    main_wrapper = Main_wrapper(SCRIPT_DIR, f"{SOURCE_DIR}{MAIN_FILE}", OUT_FILE)
    main_wrapper.wrap()

class Test_wrappers(unittest.TestCase):

    def test_f77(self):
        copy_name = f"{SOURCE_DIR}{TEST_DATA_FILE_F77}.qawa_copy"
        if does_file_exist(copy_name): 
            unwrap_file(copy_name)
        test_subroutines("Testing f77 subroutines", TEST_DATA_FILE_F77)
        test_functions("Testing f77 functions", TEST_DATA_FILE_F77)
        compare(self, TEST_DATA_FILE_F77)
        unwrap_file(copy_name)


    def test_f90(self):
        copy_name = f"{SOURCE_DIR}{TEST_DATA_FILE_F90}.qawa_copy"
        if does_file_exist(copy_name): 
            unwrap_file(copy_name)
        test_subroutines("Testing f90 subroutines", TEST_DATA_FILE_F90)
        test_functions("Testing f90 functions", TEST_DATA_FILE_F90)
        compare(self, TEST_DATA_FILE_F90)
        unwrap_file(copy_name)

    
    def test_main(self):
        copy_name = f"{SOURCE_DIR}{MAIN_FILE}.qawa_copy"
        if does_file_exist(copy_name): 
            unwrap_file(copy_name)
        test_main("Testing f77 main", MAIN_FILE)
        compare(self, MAIN_FILE)
        unwrap_file(copy_name)


if __name__ == '__main__':
    unittest.main()