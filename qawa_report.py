from qawa_strings import *

class Report_generator():
    def __init__(self, QAWA_OUT):
        self.QAWA_OUT = QAWA_OUT
        #self.REPORT_OUT = 'qawa.report'
        self.lines = []
        self.units = []

    class Unit:
        def __init__(self, file, procedure, cpu_time=0, wall_time=0):
            self.file = file
            self.procedure = procedure
            self.cpu_time = float(cpu_time)
            self.wall_time = float(wall_time)
            self.no_calls = 1
            self.self_cpu_time = 0.0
            self.self_wall_time = 0.0

        def __eq__(self, other):
            if isinstance(other, Report_generator.Unit):
                return self.file == other.file and self.procedure == other.procedure
            return False

        def __str__(self):
            return f"{self.procedure:30s}{self.file:30s}" + \
                f"{self.no_calls:8d}   |" + \
                f"{self.cpu_time:14.4f}{self.wall_time:14.4f}" + \
                f"{self.cpu_time/self.wall_time:10.2f}   |" + \
                f"{self.self_cpu_time:18.4f}{self.self_wall_time:18.4f}" + \
                f"{self.self_cpu_time/self.self_wall_time if self.self_wall_time else 0:10.2f}"

        def add(self, other):
            self.cpu_time += other.cpu_time
            self.wall_time += other.wall_time
            self.no_calls += 1


    def prepare_units(self):
        self.units = []
        for line in self.lines:
            if line.lstrip().startswith('<-'):
                line = line.replace('<-', '')
                file, procedure, cpu_time, wall_time = line.split()
                cpu_time = cpu_time
                wall_time = wall_time
                unit = self.Unit(file, procedure, cpu_time, wall_time)
                if unit in self.units:
                    next(u for u in self.units if u == unit).add(unit)
                else:
                    self.units.append(unit)


    def calculate_self_times(self):
        #print(next(u for u in units if u.procedure == 'Diag8'))
        stack = []
        for line in self.lines:
            file, procedure = line.split()[1:3]
            unit = self.Unit(file, procedure)

            if unit in self.units:

                if line.lstrip().startswith('->'):
                    unit = next(u for u in self.units if u == unit)
                    stack.append(unit)

                if line.lstrip().startswith('<-'):
                    cpu_time = float(line.split()[3])
                    wall_time = float(line.split()[4])
                    stack[-1].self_cpu_time += cpu_time
                    stack[-1].self_wall_time += wall_time

                    stack.pop()
                    if len(stack) > 0:
                        stack[-1].self_cpu_time -= cpu_time
                        stack[-1].self_wall_time -= wall_time


    def prepare_times_report(self):
        self.prepare_units()

        if len(self.units) > 0:
            self.calculate_self_times()

            self.units.sort(key=lambda u: u.wall_time, reverse=True)
            unit_max_wl = self.units[0]
            unit_max_cl = max(self.units, key=lambda u: u.cpu_time)
            unit_max_s_wl = max(self.units, key=lambda u: u.self_wall_time)
            unit_max_s_cl = max(self.units, key=lambda u: u.self_cpu_time)

            file_times = f"{self.QAWA_OUT}.times"
            print(f"Preparing {file_times}...")
            with open(file_times, 'w') as f:
                f.write(f"QAWA TIMES REPORT\n")
                f.write(f"----------------------------------\n")
                f.write(f"* All times expressed in seconds\n\n")
                
                f.write(f"-------------------\n")
                f.write(f"Sums of self times:\n")
                f.write(f"-------------------\n")
                f.write(f"Wall time: {sum(u.self_wall_time for u in self.units):8.4f}\n")
                f.write(f"CPU time: {sum(u.self_cpu_time for u in self.units):8.4f}\n")
                f.write('\n')

                f.write(f"-----------------------------------\n")
                f.write(f"The most time-consuming procedures:\n")
                f.write(f"-----------------------------------\n")
                f.write(f"Wall time: {unit_max_wl.procedure} [{unit_max_wl.file}]: {unit_max_wl.wall_time:8.4f}\n")
                f.write(f"CPU time: {unit_max_cl.procedure} [{unit_max_cl.file}]: {unit_max_cl.cpu_time:8.4f}\n")
                f.write('\n')

                f.write(f"------------------------------------------------------\n")
                f.write(f"The most time-consuming procedures excluding children:\n")
                f.write(f"------------------------------------------------------\n")
                f.write(f"Wall time: {unit_max_s_wl.procedure} [{unit_max_s_wl.file}]: {unit_max_s_wl.wall_time:8.4f}\n")
                f.write(f"CPU time: {unit_max_s_cl.procedure} [{unit_max_s_cl.file}]: {unit_max_s_cl.cpu_time:8.4f}\n")
                f.write('\n')

                f.write(f"\n{''.join(['-']*(30+30+8+3))}+{''.join(['-']*(14+14+10+3))}+{''.join(['-']*(18+18+10))}\n")
                f.write(f"{'NAME':30s}{'FILE':30s}{'CALLS':>8}   |")
                f.write(f"{'CPU_TIME':>14s}{'WALL_TIME':>14s}{'C/W':>10s}   |")
                f.write(f"{'SELF_CPU_TIME':>18s}{'SELF_WALL_TIME':>18s}{'SELF_C/W':>10s}")
                f.write(f"\n{''.join(['-']*(30+30+8+3))}+{''.join(['-']*(14+14+10+3))}+{''.join(['-']*(18+18+10))}\n")
                for unit in self.units:
                    f.write(f"{unit.__str__()}\n")


    def prepare_flow_report(self):
        file_flow = f"{self.QAWA_OUT}.flow"
        print(f"Preparing {file_flow}...")
        with open(file_flow, 'w') as f:
            f.write(f"QAWA FLOW REPORT\n")
            f.write(f"----------------------------------\n")
            tab = '    '
            running_tab = ''
            for line in self.lines:
                line = line.lstrip()
                if line.startswith('->'):
                    f.write(f"{running_tab}{line.split()[2]}\n")
                    running_tab += tab
                if line.startswith('<-'):
                    running_tab = running_tab.replace(tab, '', 1)


    def read_out_file(self):
        with open(self.QAWA_OUT, 'r') as f:
            self.lines = f.readlines()

    def generate_report(self):
        self.read_out_file()
        self.prepare_flow_report()
        self.prepare_times_report()