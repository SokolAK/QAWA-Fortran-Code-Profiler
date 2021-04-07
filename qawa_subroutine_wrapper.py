import os
from qawa_strings import *
from shutil import copy
from subroutine import Subroutine
from ordered_set import OrderedSet
import re

class Subroutine_wrapper():
	def __init__(self, SCRIPT_DIR='', SOURCE_DIR='', FILES=[], SUBROUTINES=[]):
		self.SOURCE_DIR = SOURCE_DIR
		self.SCRIPT_DIR = SCRIPT_DIR
		self.FILES = FILES
		self.SUBROUTINES = SUBROUTINES

	def add_line(self, lines, i, str):
		lines.insert(i, str + '\n')
		return i + 1

	def add_wrapper(self, lines, i, wrapper):
		for line in wrapper.splitlines():
			i = self.add_line(lines, i, line)
		return i

	def make_copy(self, file):
		org_name = f"{self.SOURCE_DIR}/{file}"
		copy_name = f"{org_name}.qawa_copy"
		if not os.path.isfile(copy_name):
			copy(org_name, copy_name)

	def prepare_subroutine_wrapper(self, subroutine):
		wrapper_body = \
f"""{get_wrapper_header()}
{subroutine.signature_lines}
      use omp_lib
{subroutine.declarations_lines}
      real :: start, end
      real ( kind = 8 ) ::  wtime, wtime2
      wtime = omp_get_wtime()
      call cpu_time(start)

      !$OMP CRITICAL
      open(61,file='{self.SCRIPT_DIR}/qawa.out',
     $action='write',position='append')
      write(61,*) '-> {subroutine.file} {subroutine.name}',
     $OMP_GET_THREAD_NUM()+1, '/', OMP_GET_NUM_THREADS()
      close(61)
      !$OMP END CRITICAL

      call {get_prefix()}{subroutine.signature_lines.replace('subroutine','').replace('Subroutine','').replace('SUBROUTINE','').lstrip()}
      call cpu_time(end)
      wtime2 = omp_get_wtime()
	
      !$OMP CRITICAL
      open(61,file='{self.SCRIPT_DIR}/qawa.out',
     $action='write',position='append')
      write(61,*) '<- {subroutine.file} {subroutine.name}',
     $end-start, wtime2-wtime
      close(61)
      !$OMP END CRITICAL

      END
{get_wrapper_footer()}

"""
		if subroutine.file.lower().rstrip().endswith('.f'):
			return wrapper_body

		if subroutine.file.lower().rstrip().endswith('.f90'):
			wrapper_lines = [line.lstrip() for line in wrapper_body.split('\n')]
			for i, line in enumerate(wrapper_lines):
				line = line.lstrip() 
				if line.startswith('$') or line.startswith('&'):
					wrapper_lines[i] = line[1:]
					wrapper_lines[i-1] = f"{wrapper_lines[i-1]}&"

			wrapper_body = '\n'.join(wrapper_lines)
			return wrapper_body
		

	def prepare_file_list(self):
		files = []
		for (dirpath, dirnames, filenames) in os.walk(self.SOURCE_DIR):
			files += [os.path.join(dirpath, file).replace(self.SOURCE_DIR,'') for file in filenames]
		files = set([file for file in files if file.endswith('.f') or file.endswith('.f90')])
		#files.update([f for f in listdir(SOURCE_DIR) if isfile(join(SOURCE_DIR, f))])
		files = [f for f in files if f in self.FILES or '*' in self.FILES]
		files = [f for f in files if f"-{f}" not in self.FILES]
		print(f"FILES: {files}")
		return files


	def is_comment(self, file, line):
		if not line.strip():
			return True

		if file.strip().endswith('.f'):
			first_char = line.lower()[0]
			return first_char == 'c' or first_char == 'd' or first_char == '*' or first_char == '!'

		if file.strip().endswith('.f90'):
			first_char = line.strip().lower()[0]
			return first_char == '!'

		return False


	def is_subroutine_start(self, line):
		return line.lower().startswith('subroutine')

	def is_wrapper(self, line):
		return line.strip() == get_wrapper_header()

	def is_wrapped_subroutine(self, subroutine):
		return subroutine.startswith(get_prefix())

	def is_subroutine_on_list(self, subroutine):
		return subroutine in self.SUBROUTINES or \
			('*' in self.SUBROUTINES and f"-{subroutine}" not in self.SUBROUTINES)

	def get_subroutine_name_from_line(self, line):
		return line.strip().replace('(',' ').split()[1]

	def should_wrap(self, file, lines, i):
		line = lines[i].strip()
		return not self.is_comment(file, line) and \
			self.is_subroutine_start(line) and \
			(self.get_subroutine_name_from_line(line) in self.SUBROUTINES or \
				('*' in self.SUBROUTINES and f"-{self.get_subroutine_name_from_line(line)}" not in self.SUBROUTINES)) and \
			not self.is_wrapper(lines[i-1]) and \
			not self.is_wrapped_subroutine(self.get_subroutine_name_from_line(line))


	def process_line(self, file, lines, i):
		if self.should_wrap(file,lines,i):
			subroutine = get_subroutine_from_line(line)
			print(f"{file:20s}			{subroutine:20s}", end='')
			if self.is_subroutine_on_list(subroutine):
				j = i + 1
				while not lines[j].lstrip().lower().startswith('end'):
					j += 1
					di = self.wrap_subroutine(file, subroutine, lines, i, j)
					print('				wrapped', end='')
					i += di
			print()

		return i


	def save_file(self, file, lines):
		with open(f"{self.SOURCE_DIR}/{file}", 'w') as f:
			for line in lines:
				f.write(line)	


	def modify_stops(self):
		files = []
		for (dirpath, dirnames, filenames) in os.walk(self.SOURCE_DIR):
			files += [os.path.join(dirpath, file).replace(self.SOURCE_DIR,'') for file in filenames]
		files = set([file for file in files if file.endswith('.f') or file.endswith('.f90')])

		for file in files:
			lines = []
			with open(f"{self.SOURCE_DIR}/{file}", 'r') as f:
				lines = f.readlines()

			for i,line in enumerate(lines):
				line = line.lower()
				if line.lstrip().startswith('stop'):

					lines[i] = line.replace(line[line.index('stop'):], 'return\n')

					while lines[i].strip().endswith('&') or \
						lines[i+1].strip().startswith('$') or lines[i+1].strip().startswith('&'):
						lines[i+1] = ''
						i += 1

			self.save_file(file, lines)

						

	def modify_ends(self, lines, subroutines):
		for i, line in enumerate(lines):
			if 'end subroutine' in line.lower():
				words = line.strip().split()
				if len(words) == 3:
					name = line.strip().split()[2]
					for subroutine in subroutines:
						if subroutine.name.lower() == name.lower():
							lines[i] = line.replace(name, f"{get_prefix()}{name}")


	def wrap_subroutine(self, lines, subroutine):
		self.make_copy(subroutine.file)
		i = 0

		while not (lines[i].strip().lower().startswith('subroutine') and \
				subroutine.name == self.get_subroutine_name_from_line(lines[i])):
			i += 1
		
		lines[i] = lines[i].replace(subroutine.name, f"{get_prefix()}{subroutine.name}")
		line = lines[i]
		
		splitted_line = line.split('(')
		if len(splitted_line) > 1:
			lines[i] = splitted_line[0]
			lines.insert(i+1, f"({splitted_line[1]}")

			if subroutine.file.strip().endswith('.f'):
				lines[i] = f"{lines[i]}\n"
				lines[i+1] = f"     ${lines[i+1]}"
			if subroutine.file.strip().endswith('.f90'):
				lines[i] = f"{lines[i]}&\n"

		#subroutine.declarations = self.get_declarations(lines,i,subroutine)
		wrapper = self.prepare_subroutine_wrapper(subroutine).split('\n')
		wrapper = [w+'\n' for w in wrapper]
		lines[i:i] = wrapper

		#print(lines[i])

	def find_subroutines(self, file, lines):
		subroutines = []
		i = 0
		while i < len(lines):
			line = lines[i]
			if self.should_wrap(file, lines, i):
				# line = line.strip()
				# name = line[:line.find('(')]
				# name = name.split()[-1]
				name = self.get_subroutine_name_from_line(line)

				signature_lines = []
				signature_lines.append(line)
				signature = name + line[line.find('('):].replace('&', '').strip()
				while not signature.endswith(')'):
					i += 1
					signature += f"{lines[i].replace('&', '').replace('$','').strip()}"
					signature_lines.append(lines[i])
				signature_lines = ''.join(signature_lines)

				args = []
				args_str = signature.replace(name,'') \
					.replace('(', '') \
					.replace(')', '') \
					.replace('&', '') \
					.replace(' ', '')
				args = args_str.split(',')	

				i += 1
				declarations_lines = []
				key_words = ['use','include','data','implicit','character','real','double','integer','dimension','logical','complex','parameter','type']
				end_of_declarations = False
				while not end_of_declarations:
					#print(lines[i])
					end_of_declarations = True
					for key_word in key_words:
						#print(key_word)
						#if re.search(rf"\b{key_word}\b", lines[i].lower().replace(',',' ').replace('(',' ').replace(')',' ')) or \
						if lines[i].strip().lower().startswith(key_word) or \
								lines[i].strip() == '' or \
								self.is_comment(file, lines[i]) or \
								lines[i].strip().startswith('$') or \
								lines[i].strip().startswith('&') or \
								lines[i-1].strip().endswith('&'):

							end_of_declarations = False
							if not self.is_comment(file, lines[i]):	
								declarations_lines.append(lines[i])
							#print(True)
							break
					i += 1

				declarations_lines = ''.join(declarations_lines)
				subroutines.append(Subroutine(file,name,signature,signature_lines,args,declarations_lines))
			i += 1
		return subroutines


	def wrap(self):
		files = self.prepare_file_list()

		for file in files:
			lines = []
			with open(f"{self.SOURCE_DIR}/{file}", 'r') as f:
				lines = f.readlines()

			subroutines = self.find_subroutines(file, lines)
			for subroutine in subroutines:
				print(subroutine, end='')
				self.wrap_subroutine(lines, subroutine)
				print('wrapped')

			self.modify_ends(lines, subroutines)

			self.save_file(file,lines)

		self.modify_stops()


