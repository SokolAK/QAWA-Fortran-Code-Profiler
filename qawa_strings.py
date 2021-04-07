def print_banner():
	print(f"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     )))    QAWA* Fortran  
    C\\_/    Code Profiler 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*Quasi-Aspect-Weaving Approach
""")

def get_wrapper_header():
	return '!start qawa wrapper ##########################################'

def get_wrapper_footer():
	return '!end qawa wrapper ############################################'

def get_prefix():
	return 'qawa_'