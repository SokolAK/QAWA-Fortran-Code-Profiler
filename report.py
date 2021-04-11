from strings import *
from utils import get_separator, read_file

#Column widths
cw = [24,20,4,6, 14,14,10, 14,14,10]

class Report_generator():
    def __init__(self, QAWA_OUT):
        self.QAWA_OUT = QAWA_OUT
        #self.REPORT_OUT = 'qawa.report'
        self.lines = []
        self.units = []

    class Unit:
        def __init__(self, file, procedure, typ, cpu_time=0, wall_time=0):
            self.file = file
            self.procedure = procedure
            self.typ = typ
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
            return f"{self.procedure:{cw[0]}s} | {self.file:{cw[1]}s} | " + \
                f"{self.typ:^{cw[2]}s} | " + \
                f"{self.no_calls:{cw[3]}d} | " + \
                f"{self.cpu_time:{cw[4]}.4f} | {self.wall_time:{cw[5]}.4f} | " + \
                f"{self.cpu_time/self.wall_time:{cw[6]}.2f} | " + \
                f"{self.self_cpu_time:{cw[7]}.4f} | {self.self_wall_time:{cw[8]}.4f} | " + \
                f"{self.self_cpu_time/self.self_wall_time if self.self_wall_time else 0:{cw[9]}.2f}"

        def add(self, other):
            self.cpu_time += other.cpu_time
            self.wall_time += other.wall_time
            self.no_calls += 1


    def prepare_units(self):
        self.units = []
        for line in self.lines:
            if line.lstrip().startswith('<-'):
                line = line.replace('<-', '')
                file, procedure, typ, cpu_time, wall_time = line.split()
                cpu_time = cpu_time
                wall_time = wall_time
                unit = self.Unit(file, procedure, typ, cpu_time, wall_time)
                if unit in self.units:
                    next(u for u in self.units if u == unit).add(unit)
                else:
                    self.units.append(unit)


    def calculate_self_times(self):
        stack = []
        for line in self.lines:
            file, procedure, typ = line.split()[1:4]
            unit = self.Unit(file, procedure, typ)

            if unit in self.units:

                if line.lstrip().startswith('->'):
                    unit = next(u for u in self.units if u == unit)
                    stack.append(unit)

                if line.lstrip().startswith('<-'):
                    cpu_time = float(line.split()[4])
                    wall_time = float(line.split()[5])
                    stack[-1].self_cpu_time += cpu_time
                    stack[-1].self_wall_time += wall_time

                    stack.pop()
                    if len(stack) > 0:
                        stack[-1].self_cpu_time -= cpu_time
                        stack[-1].self_wall_time -= wall_time


    def get_summary(self):
        unit_max_wl = max(self.units, key=lambda u: u.wall_time)
        unit_max_cl = max(self.units, key=lambda u: u.cpu_time)
        unit_max_s_wl = max(self.units, key=lambda u: u.self_wall_time)
        unit_max_s_cl = max(self.units, key=lambda u: u.self_cpu_time)
        return f"""QAWA TIMES REPORT
--------------------------------
* All times expressed in seconds

-------------------
Sums of self times:
-------------------
Wall time: {sum(u.self_wall_time for u in self.units):8.4f}
CPU time: {sum(u.self_cpu_time for u in self.units):8.4f}

-----------------------------------
The most time-consuming procedures:
-----------------------------------
Wall time: {unit_max_wl.procedure} [{unit_max_wl.file}]: {unit_max_wl.wall_time:8.4f}
CPU time: {unit_max_cl.procedure} [{unit_max_cl.file}]: {unit_max_cl.cpu_time:8.4f}

------------------------------------------------------
The most time-consuming procedures excluding children:
------------------------------------------------------
Wall time: {unit_max_s_wl.procedure} [{unit_max_s_wl.file}]: {unit_max_s_wl.wall_time:8.4f}
CPU time: {unit_max_s_cl.procedure} [{unit_max_s_cl.file}]: {unit_max_s_cl.cpu_time:8.4f}
"""


    def get_times_table(self,sorter):
        self.units.sort(key=sorter, reverse=True)
        table_separator = f"{get_separator('-',cw[0]+1)}"
        for i in range(1, len(cw), 1):
            table_separator += f"+{get_separator('-',cw[i]+2)}"
        table_header = f"{'NAME':{cw[0]}s} | {'FILE':{cw[1]}s} | {'TYPE':{cw[2]}s} | {'CALLS':>{cw[3]}} | " + \
            f"{'CPU_TIME':>{cw[4]}s} | {'WALL_TIME':>{cw[5]}s} | {'C/W':>{cw[6]}s} | " + \
            f"{'SELF_CPU_TIME':>{cw[7]}s} | {'SELF_WALL_TIME':>{cw[8]}s} | {'SELF_C/W':>{cw[9]}s}"

        newline = '\n'
        table = f"""
{table_separator}
{table_header}
{table_separator}
{newline.join(u.__str__() for u in self.units)}
{table_separator}
"""
        return table


    def prepare_times_report(self):
        self.prepare_units()

        if len(self.units) > 0:
            file_times = f"{self.QAWA_OUT}.times"
            print(f"Preparing {file_times}...")

            self.calculate_self_times()

            with open(file_times, 'w') as f:
                f.write(self.get_summary())
                f.write(f"\n\nEXECUTION TIMES sorted by WALL TIME:{''.join([' ']*47)}V DESCENDING V")
                f.write(self.get_times_table(lambda u: u.wall_time))
                f.write(f"\n\nEXECUTION TIMES sorted by SELF WALL TIME:{''.join([' ']*89)}V DESCENDING V")
                f.write(self.get_times_table(lambda u: u.self_wall_time))


    def prepare_flow_report(self):
        file_flow = f"{self.QAWA_OUT}.flow"
        print(f"Preparing {file_flow}...")
        with open(file_flow, 'w') as f:
            f.write(f"QAWA FLOW REPORT\n")
            f.write(f"----------------\n")
            tab = '    '
            running_tab = ''
            for line in self.lines:
                line = line.lstrip()
                if line.startswith('->'):
                    f.write(f"{running_tab}{line.split()[2]}\n")
                    running_tab += tab
                if line.startswith('<-'):
                    running_tab = running_tab.replace(tab, '', 1)


    def prepare_short_flow_report(self):
        file_flow = f"{self.QAWA_OUT}.short_flow"
        print(f"Preparing {file_flow}...")
        lines = []
        with open(f"{self.QAWA_OUT}.flow", 'r') as f:
            lines = f.readlines()
        lines = lines [2:]

        for n in range(1, int(len(lines)/2+1), 1):
            i = 0
            while i < len(lines) - n:
                flag = True
                no = 1
                i0 = i
                while flag:
                    for j in range(n):
                        if i + j + n > len(lines)-1:
                            flag = False
                            break
                        if not lines[i+j] == lines[i+j+n]:
                            flag = False
                            break
                    if flag == True:
                        no += 1
                        del lines[i:i+n]
                    else:
                        i += 1
                        del lines[i0+1:i]
                        if no > 1:
                            max_length = max([len(line.rstrip()) for line in lines[i0:i0+n]])
                            for j in range(i0, i0 + n):
                                lines[j] = f"{lines[j].rstrip()}{''.join([' ']*(max_length - len(lines[j].rstrip())))}   |\n"
                            lines[i0] = f"{lines[i0].rstrip()}x{no}\n"

        with open(file_flow, 'w') as f:
            f.write(f"QAWA SHORT FLOW REPORT\n")
            f.write(f"----------------------\n")
            for line in lines:
                f.write(line)


    def generate_report(self):
        self.lines = read_file(self.QAWA_OUT)
        self.prepare_flow_report()
        self.prepare_short_flow_report()
        self.prepare_times_report()