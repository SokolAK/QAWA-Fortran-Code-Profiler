
class Report_generator():
	def __init__(self, QAWA_OUT):
		self.QAWA_OUT = QAWA_OUT
		#self.REPORT_OUT = 'qawa.report'
		self.lines = []
		self.units = {}

	class Unit:
		def __init__(self, file, function, cpu_time, wall_time):
			self.file = file
			self.function = function
			self.cpu_time = cpu_time
			self.wall_time = wall_time
			self.no_calls = 1

		def __eq__(self, other):
			if isinstance(other, Report_generator.Unit):
				return self.file == other.file and self.function == other.function
			return False

		def __str__(self):
			return f"{self.file:30s}{self.function:30s}" + \
				f"{str(self.no_calls):7s}" + \
				f"{str(round(self.cpu_time, 4)):12s}{str(round(self.wall_time, 4)):12s}" + \
				f"{float(self.cpu_time)/float(self.wall_time):2.2f}"

		def add(self, other):
			self.cpu_time += other.cpu_time
			self.wall_time += other.wall_time
			self.no_calls += 1


	def calculate_total_times(self):
		units = []
		for line in self.lines:
			if line.lstrip().startswith('<-'):
				line = line.replace('<-', '')
				file, function, cpu_time, wall_time = line.split()
				cpu_time = float(cpu_time)
				wall_time = float(wall_time)
				unit = self.Unit(file, function, cpu_time, wall_time)
				if unit in units:
					next(u for u in units if u == unit).add(unit)
				else:
					units.append(unit)

		units.sort(key=lambda u: u.wall_time, reverse=True)

		# wall_time = 0
		# cpu_time = 0
		# for unit in units:
		# 	wall_time += unit.wall_time
		# 	cpu_time += unit.cpu_time

		# print(f"Sum of wall times: {wall_time}")
		# print(f"Sum of cpu times: {cpu_time}")
		# print()

		file_times = f"{self.QAWA_OUT}.times"
		print(f"Preparing {file_times}...")
		with open(file_times, 'w') as f:
			f.write(f"{'FILE':30s}{'NAME':30s}{'CALLS':7}{'CPU_TIME':12s}{'WALL_TIME':12s}C/W\n")
			f.write(f"{''.join(['-'] * (30+30+7+12+12+4))}\n")
			for unit in units:
				f.write(f"{unit.__str__()}\n")

		file_flow = f"{self.QAWA_OUT}.flow"
		print(f"Preparing {file_flow}...")
		with open(file_flow, 'w') as f:
			tab = '    '
			running_tab = ''
			for line in self.lines:
				line = line.lstrip()
				if line.startswith('->'):
					running_tab += tab
					f.write(f"{running_tab}{line.split()[2]}\n")
				if line.startswith('<-'):
					running_tab = running_tab[:-4]


	def read_out_file(self):
		with open(self.QAWA_OUT, 'r') as f:
			self.lines = f.readlines()

	def generate_report(self):
		self.read_out_file()
		self.calculate_total_times()