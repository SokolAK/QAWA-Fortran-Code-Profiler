def get_banner():
	return f"""~~~ ))) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   F\_/  QAWA Fortran-Code-Profiler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

def get_wrapper_header():
	return '!start qawa wrapper ##########################################'

def get_wrapper_footer():
	return '!end qawa wrapper ############################################'

def get_fragment_header(str=''):
	return f'!start qawa {str} ##################################'

def get_fragment_footer(str=''):
	return f'!end qawa {str} ##################################'

def get_prefix():
	return 'qawa_'