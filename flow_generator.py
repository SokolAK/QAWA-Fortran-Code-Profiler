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

    # class Procedure:
    #     def __init__(self, file, name, typ):
    #         self.file = file
    #         self.name = name
    #         self.typ = typ
    #         self.thread = 0
    #         self.max_threads = 0
    #         self.ctime = 0
    #         self.wtime = 0
    #         self.no_calls = 0
    #         self.self_ctime = 0.0
    #         self.self_wtime = 0.0
    #     def __str__(self):
    #         return f"{self.name:15s} {self.thread:1d}/{self.max_threads:1d}"
    #     def __eq__(self, other):
    #         return self.name == other.name and self.file == other.file


    # class Stack():
    #     def __init__(self, th=0):
    #         self.th = th
    #         self.frames = []
    #     def __str__(self):
    #         string = ''
    #         for frame in self.frames:
    #             if isinstance(frame, list):
    #                 i = 0
    #                 flag = True
    #                 while flag:
    #                     flag = False
    #                     for sub_stack in frame:
    #                         if i < len(sub_stack):
    #                             string += f"{sub_stack.th} {sub_stack.frames[i]}{''.join([' ']*15)}"
    #                             flag = True
    #                         else:
    #                             string += f"{sub_stack.th} {'':19s}{''.join([' ']*15)}"
    #                     string += '\n'
    #                     i += 1

    #             else:
    #                 string += f"{''.join([' ']*15*self.th)}{self.th} {frame}\n"


    #         return string
    #     # def __repr__(self):
    #     #     return str(self)

    #         return string
    #     def append(self, frame):
    #         self.frames.append(frame)
    #     def pop(self):
    #         self.frames.pop()
    #     def __len__(self):
    #         return len(self.frames)


    def generate_report(self):
        lines = read_file(self.QAWA_OUT)
        threads_nums = get_threads_nums(lines)
        paths = self.prepare_paths(lines, threads_nums)
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


    # def show_stack(self, lines):
    #     parallel = False
    #     sub_stacks = []
    #     stack = self.Stack()
    #     for line in lines:

    #         if self.is_enter(line):
    #             dire, file, name, typ, thread, max_threads = self.unpack_enter_line(line)
    #         if self.is_exit(line):
    #             dire, file, name, typ, thread, max_threads, stime, ctime, wtime = self.unpack_exit_line(line)   

    #         if max_threads > 1 and parallel == False:
    #             for i in range(max_threads):
    #                 sub_stacks.append(self.Stack(i))
    #             stack.append(sub_stacks)
    #             parallel = True

    #         if max_threads == 1 and parallel == True:
    #             sub_stacks = []
    #             stack.pop()
    #             parallel = False


    #         if parallel == False:
    #             if self.is_enter(line):
    #                 proc = self.Procedure(file,name,typ)
    #                 stack.append(proc)
    #             if self.is_exit(line):

    #                 stack.pop()

    #         if parallel == True:
    #             if self.is_enter(line):
    #                 proc = self.Procedure(file,name,typ)
    #                 sub_stacks[thread-1].append(proc)
    #             if self.is_exit(line):
    #                 sub_stacks[thread-1].pop()


    #         print(''.join(['-']*200))
    #         print(stack)

    def prepare_paths(self, lines, threads_nums):
        paths = []
        for th in threads_nums:
            paths.append([])

        for line in lines:
            if is_enter(line):
                dire, file, name, typ, thread, max_threads = unpack_enter_line(line)
            if is_exit(line):
                dire, file, name, typ, thread, max_threads, stime, ctime, wtime = unpack_exit_line(line)

            if thread == 1 and max_threads == 1:
                for path in paths:
                    path.append(line)
            else:
                paths[thread-1].append(line)

        return paths



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

        #with open(file_flow, 'w') as f:
        #    f.write(f"{file_flow}\n")
        #    f.write(f"{''.join(['-']*len(file_flow))}\n\n")

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
