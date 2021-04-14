# QAWA CONFIGURATION
########################################################################
SOURCE_DIR = '/home/adam.sokol/QCHEM/GAMMCOR_GitLab/SOURCE/'
MAIN_FILE = SOURCE_DIR + 'mainp.f'
SUBROUTINES_FILES = ['*', '-timing.f90']
SUBROUTINES = ['*', '-add_to_Sorter', '-dump_Batch', '-get_from_Sorter', \
                '-triang_to_sq2', '-triang_to_sq', '-ints_modify']
FUNCTIONS_FILES = ['*']
FUNCTIONS = ['*','-FRDM2']
########################################################################
#
# HELP
#
# SOURCE_DIR        -- path to your source files
# MAIN_FILE         -- path to your main file
# SUBROUTINES_FILES -- list of files with subroutines to wrap
# SUBROUTINES       -- list of subroutines to wrap
# FUNCTIONS_FILES   -- list of files with functions to wrap
# FUNCTIONS         -- list of functions to wrap
#
# You can use the following notation in SUBROUTINES_FILES, SUBROUTINES,
# FUNCTIONS_FILES and FUNCTIONS:
# 'name'  -- adds file/procedure 'name' to the wrapping list
# '-name' -- excludes file/procedure 'name' from the wrapping list
# '*'     -- adds all files from SOURCE_DIR or procedures from
#            SUBROUTINES_FILES/FUNCTIONS_FILES to the wrapping list