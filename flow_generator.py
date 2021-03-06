from strings import *
import os
import re
from utils import *
from line_utils import *
import datetime

#Column widths
cw = [11, 11, 6, 11, 11, 6, 5, 7]

class Flow_generator():
    def __init__(self, QAWA_OUT):
        self.QAWA_OUT = QAWA_OUT
        self.lines = []
        self.units = []


    def generate_report(self):
        lines = read_file(self.QAWA_OUT)
        threads_nums = get_threads_nums(lines)
        paths = prepare_paths(lines, max(threads_nums))
        flows = self.prepare_flows(paths)
        short_flows = self.roll_up_flows(flows)
        self.save_flows(lines, len(paths))
        self.save_flows(lines, len(paths), rollup=True)


    def roll_up_flows(self, flows):
        short_flows = []
        for num, flow in enumerate(flows):
            short_flows.append(self.roll_up_flow(flow))
        return short_flows


    def roll_up_flow(self, flow):
        for n in range(1, int(len(flow)/2+1), 1):
            i = 0
            while i < len(flow) - n:
                block_found = True
                no = 1
                i0 = i
                while block_found:
                    for j in range(n):
                        if i + j + n > len(flow)-1:
                            block_found = False
                            break
                        if not flow[i+j] == flow[i+j+n]:
                            block_found = False
                            break
                    if block_found == True:
                        no += 1
                        del flow[i:i+n]
                    else:
                        i += 1
                        del flow[i0+1:i]
                        if no > 1:
                            max_length = max([len(line.rstrip()) for line in flow[i0:i0+n]])
                            for j in range(i0, i0 + n):
                                flow[j] = f"{flow[j].rstrip()}{''.join([' ']*(max_length - len(flow[j].rstrip())))}   |"
                            flow[i0] = f"{flow[i0].rstrip()}x{no}"
        return flow

    def prepare_flows(self, paths):
        flows = []
        for th in range(len(paths)):
            flows.append([])
        tab = '.   '
        running_tab = ''

        for i,path in enumerate(paths):
            for line in path:
                line = line.lstrip()
                if line.startswith('->'):
                    dire, file, name, typ, thread, max_threads = unpack_enter_line(line)
                    flows[i].append(f"{running_tab}{name}({thread})\n")
                    running_tab += tab
                if line.startswith('<-'):
                    running_tab = running_tab.replace(tab, '', 1)
        return flows


    def save_flows(self, lines, paths_num, rollup=False):
        file_flow = f"{self.QAWA_OUT}.flow"
        if rollup:
            file_flow += '_short'
        print(f"Preparing {file_flow}...")
        file_flow += '.md'

        new_lines = []
        i = 0
        tab = '.   '
        running_tabs = ['#1 '] * paths_num

        while i < len(lines):
            parallel_flows = []
            for th in range(paths_num):
                parallel_flows.append([])

            line = lines[i].rstrip()
            dire, file, name, typ, thread, max_threads, stime, ctime, wtime = unpack_line(line)

            # SEQUENTIAL
            # ----------------------------------------------------------------------
            if max_threads == 1:
                if dire == '->':
                    new_lines.append(f"{running_tabs[0]}{name}")
                    running_tabs[0] += tab
                if dire == '<-':
                    running_tabs[0] = running_tabs[0].replace(tab, '', 1)
            # PARALLEL
            # ----------------------------------------------------------------------
            else:
                threads = max_threads

                for r in range(0, len(running_tabs)):
                    running_tabs[r] = f"#{str(r+1)}{running_tabs[0][2:]}"

                while max_threads > 1:
                    string = f"{running_tabs[thread-1]}{name}"
                    if dire == '->':
                        string = f"{running_tabs[thread-1]}{name}"
                        parallel_flows[thread-1].append(string)
                        running_tabs[thread-1] += tab
                    if dire == '<-':
                        running_tabs[thread-1] = running_tabs[thread-1].replace(tab, '', 1)

                    i += 1
                    line = lines[i].rstrip()
                    dire, file, name, typ, thread, max_threads, stime, ctime, wtime = unpack_line(line)


                if rollup:                
                    parallel_flows = self.roll_up_flows(parallel_flows)


                max_length = 0
                i0 = len(new_lines)
                lines_num = len(max(parallel_flows, key=len))
                for j in range(lines_num):
                    new_line = False
                    for flow in parallel_flows:
                        if j < len(flow):
                            if not new_line:
                                new_lines.append('')
                            new_lines[-1] = new_lines[-1] + f"{flow[j].rstrip():50s}"   
                            max_length = max(max_length, len(new_lines[-1].rstrip()))
                            new_line = True

                
                new_lines = [line.rstrip() for line in new_lines]

                new_lines.insert(i0, f"PARALLEL {threads} {''.join(['=']*max_length)}")            
                new_lines.append(f"SEQUENTIAL {''.join(['-']*max_length)}")    
                i -= 1
            i += 1
        

        if rollup:               
            new_lines = self.roll_up_flow(new_lines)

        new_lines = [line + '\n' for line in new_lines]

        title = f"QAWA CHAINS REPORT"
        details = f"Details: rollup={rollup}"
        header = (f"# {title}\n")
        header += f"#### {details}\n"
        header += f"#### File: {file_flow}\n"
        header += f"#### Date: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        header += f"{''.join(['-']*len(details))}\n\n"
        new_lines.insert(0, '```\n')
        new_lines.append('```')

        save_file(file_flow,new_lines,header,mode='w') 
