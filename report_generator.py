from strings import *
from utils import get_separator, read_file, save_file

#Column widths
cw = [24,20,4,6, 14,14,10, 14,14,10]

class Report_generator():
    def __init__(self, QAWA_OUT):
        self.QAWA_OUT = QAWA_OUT
        #self.REPORT_OUT = 'qawa.report'
        self.lines = []
        self.units = []
        self.overhead = 0

    class Unit:
        def __init__(self, file, procedure, typ, cpu_time=0, wall_time=0):
            self.file = file
            self.procedure = procedure
            self.typ = typ
            self.cpu_time = cpu_time
            self.wall_time = wall_time
            self.no_calls = 1
            self.self_cpu_time = 0.0
            self.self_wall_time = 0.0
            self.overhead = 0
        def __eq__(self, other):
            if isinstance(other, Report_generator.Unit):
                return self.file == other.file and self.procedure == other.procedure
            return False
        def __str__(self):
            return f"{self.procedure:{cw[0]}s} | {self.file:{cw[1]}s} | " + \
                f"{self.typ:^{cw[2]}s} | " + \
                f"{self.no_calls:{cw[3]}d} | " + \
                f"{self.cpu_time:{cw[4]}.4f} | {self.wall_time:{cw[5]}.4f} | " + \
                f"{self.cpu_time/self.wall_time:{cw[6]}.4f} | " + \
                f"{self.self_cpu_time:{cw[7]}.4f} | {self.self_wall_time:{cw[8]}.4f} | " + \
                f"{self.self_cpu_time/self.self_wall_time if self.self_wall_time else 0:{cw[9]}.4f}"
        def add(self, other):
            self.cpu_time += other.cpu_time
            self.wall_time += other.wall_time
            self.no_calls += 1


    def generate_report(self):
        self.lines = read_file(self.QAWA_OUT)
        self.calculate_overhead()
        self.prepare_flow_report()
        self.prepare_short_flow_report()
        self.prepare_times_report()
        self.prepare_chains_report()


    def unpack_line(self, line):
        if line.startswith('->'):
            direction, file, procedure, typ, thread, no_threads  = line.split()
            return file, procedure, typ, int(thread), int(no_threads)
        else:
            direction, file, procedure, typ, thread, no_threads, sys_time, cpu_time, wall_time = line.split()
            cpu_time, wall_time = float(cpu_time), float(wall_time)
            m = cpu_time / wall_time if wall_time > 0 else 1
            wall_time -= self.overhead
            cpu_time = wall_time * m
            return file, procedure, typ, cpu_time, wall_time


    def calculate_overhead(self):
        self.overhead = 0.00162
        for line in self.lines:
            if line.startswith('<-'):
                self.overhead = min(self.overhead, float(line.split()[-1]))
        return self.overhead


    def prepare_units(self):
        self.units = []
        for line in self.lines:
            if line.lstrip().startswith('<-'):
                #line = line.replace('<-', '')
                file, procedure, typ, cpu_time, wall_time = self.unpack_line(line)
                #cpu_time = float(cpu_time) - self.calculate_overhead()
                #wall_time = float(wall_time) - self.calculate_overhead()
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
                    file, procedure, typ, cpu_time, wall_time = self.unpack_line(line)
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
            f"{'CPU TIME':>{cw[4]}s} | {'WALL TIME':>{cw[5]}s} | {'C/W':>{cw[6]}s} | " + \
            f"{'SELF CPU TIME':>{cw[7]}s} | {'SELF WALL TIME':>{cw[8]}s} | {'SELF C/W':>{cw[9]}s}"

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
            f.write(f"----------------\n\n")
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
        lines = read_file(f"{self.QAWA_OUT}.flow")
        lines = lines [3:]

        for n in range(1, int(len(lines)/2+1), 1):
            i = 0
            while i < len(lines) - n:
                block_found = True
                no = 1
                i0 = i
                while block_found:
                    for j in range(n):
                        if i + j + n > len(lines)-1:
                            block_found = False
                            break
                        if not lines[i+j] == lines[i+j+n]:
                            block_found = False
                            break
                    if block_found == True:
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

        lines.insert(0, f"----------------------\n\n")
        lines.insert(0, f"QAWA SHORT FLOW REPORT\n")
        save_file(file_flow,lines)


    def prepare_chains_report(self):
        file_chains = f"{self.QAWA_OUT}.chains"
        print(f"Preparing {file_chains}...")

        chains = {}
        chain = []
        previous_procedure = ''
        max_chain_length = 0
        for line in self.lines:
            procedure_name = line.split()[2]
            if line.lstrip().startswith('->'):
                chain.append(procedure_name)
                chain_string = f"{' -> '.join(chain)}"
                if not chain_string in chains:
                    chains[chain_string] = {'count':0, 'wtime':0, 'ctime':0}
                    max_chain_length = max(max_chain_length, len(chain_string.strip()))

            if line.lstrip().startswith('<-'):
                file, procedure_name, typ, ctime, wtime = self.unpack_line(line)
                chain_string = f"{' -> '.join(chain)}"
                chains[chain_string]['count'] += 1
                chains[chain_string]['wtime'] += wtime
                chains[chain_string]['ctime'] += ctime
                chain.pop()
                if len(chain) > 0:
                    chain_string = f"{' -> '.join(chain)}"
                    chains[chain_string]['ctime'] -= ctime
                    chains[chain_string]['wtime'] -= wtime
            previous_procedure = procedure_name

        chains = dict(sorted(chains.items(), key=lambda item: item[1]['wtime'], reverse=True))

        with open(file_chains, 'w') as f:
            f.write(f"QAWA CHAINS REPORT\n")
            f.write(f"--------------------------------------------------------------\n")
            f.write(f"* W-TIME = wall time, C-TIME = CPU time, C/W = C-TIME / W-TIME\n")
            f.write(f"* All times expressed in seconds\n\n")
            f.write(f"V  DESC.  V\n")
            f.write(f"{'SELF W-TIME':>11s}  {'SELF C-TIME':>11s}  {'C/W':>6s}  {'CALLS':>6s}  {'CHAIN'}\n")  
            f.write(f"{''.join(['-']*(11 + 2 + 11 + 2 + 9 + 2 + 6 + 2 + max_chain_length))}\n")
            for name, details in chains.items():
                f.write(f"{details['wtime']:11.4f}  {details['ctime']:11.4f}  ")
                f.write(f"{details['ctime']/details['wtime'] if details['wtime'] > 0 else 0:6.2f}  ")
                f.write(f"{details['count']:6d}  {name}\n")  
