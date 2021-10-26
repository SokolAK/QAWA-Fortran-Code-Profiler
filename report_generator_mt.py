from strings import *
import os
import re
from utils import get_separator, read_file, save_file, get_substring_symbol
import datetime

#Column widths
cw = [11, 11, 6, 11, 11, 6, 5, 7]

class Report_generator():
    def __init__(self, QAWA_OUT):
        self.QAWA_OUT = QAWA_OUT
        self.lines = []
        self.units = []

    class Procedure:
        def __init__(self, file, name, typ):
            self.file = file
            self.name = name
            self.typ = typ
            self.thread = 0
            self.max_threads = 0
            self.ctime = 0
            self.wtime = 0
            self.no_calls = 0
            self.self_ctime = 0.0
            self.self_wtime = 0.0
        def __str__(self):
            return f"{self.name:15s} {self.thread:1d}/{self.max_threads:1d}"
        def __eq__(self, other):
            return self.name == other.name and self.file == other.file
        # def __repr__(self):
        #     return str(self)


    class Stack():
        def __init__(self, th=0):
            self.th = th
            self.frames = []
        def __str__(self):
            string = ''
            for frame in self.frames:
                if isinstance(frame, list):
                    i = 0
                    flag = True
                    while flag:
                        flag = False
                        for sub_stack in frame:
                            if i < len(sub_stack):
                                string += f"{sub_stack.th} {sub_stack.frames[i]}{''.join([' ']*15)}"
                                flag = True
                            else:
                                string += f"{sub_stack.th} {'':19s}{''.join([' ']*15)}"
                        string += '\n'
                        i += 1

                else:
                    string += f"{''.join([' ']*15*self.th)}{self.th} {frame}\n"


            return string
        # def __repr__(self):
        #     return str(self)

            return string
        def append(self, frame):
            self.frames.append(frame)
        def pop(self):
            self.frames.pop()
        def __len__(self):
            return len(self.frames)


    def generate_report(self):
        lines = read_file(self.QAWA_OUT)
        threads_nums = self.get_threads_nums(lines)
        #self.show_stack(lines)
        #self.prepare_chains_report(lines)
        paths = self.prepare_paths(lines, threads_nums)
        flows = self.prepare_flows(paths)
        short_flows = self.roll_up_flows(flows)
        self.save_flows(lines, len(paths))
        self.save_flows(lines, len(paths), rollup=True)
        chains = self.prepare_chains(lines, len(paths))
        self.save_chains(f"{self.QAWA_OUT}.chains", chains, sort_key='self_wtime', reverse=False)
        self.save_chains(f"{self.QAWA_OUT}.chains", chains, sort_key='self_wtime', reverse=True)
        self.save_chains(f"{self.QAWA_OUT}.chains", chains, sort_key='wtime', reverse=False)
        self.save_chains(f"{self.QAWA_OUT}.chains", chains, sort_key='wtime', reverse=True)
        rolled_chains = self.rollup_chains(chains)
        self.save_chains(f"{self.QAWA_OUT}.chains", rolled_chains, sort_key='self_wtime', rollup=True, reverse=True)
        self.save_chains(f"{self.QAWA_OUT}.chains", rolled_chains, sort_key='wtime', rollup=True, reverse=True)


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
                if self.is_enter(line):
                    dire, file, name, typ, thread, max_threads = self.unpack_enter_line(line)
                    flows[i].append(f"{running_tab}{name}({thread})\n")
                    running_tab += tab
                if self.is_exit(line):
                    running_tab = running_tab.replace(tab, '', 1)
        return flows


    def show_stack(self, lines):
        parallel = False
        sub_stacks = []
        stack = self.Stack()
        for line in lines:

            if self.is_enter(line):
                dire, file, name, typ, thread, max_threads = self.unpack_enter_line(line)
            if self.is_exit(line):
                dire, file, name, typ, thread, max_threads, stime, ctime, wtime = self.unpack_exit_line(line)   

            if max_threads > 1 and parallel == False:
                for i in range(max_threads):
                    sub_stacks.append(self.Stack(i))
                stack.append(sub_stacks)
                parallel = True

            if max_threads == 1 and parallel == True:
                sub_stacks = []
                stack.pop()
                parallel = False


            if parallel == False:
                if self.is_enter(line):
                    proc = self.Procedure(file,name,typ)
                    stack.append(proc)
                if self.is_exit(line):

                    stack.pop()

            if parallel == True:
                if self.is_enter(line):
                    proc = self.Procedure(file,name,typ)
                    sub_stacks[thread-1].append(proc)
                if self.is_exit(line):
                    sub_stacks[thread-1].pop()


            print(''.join(['-']*200))
            print(stack)


    def prepare_paths(self, lines, threads_nums):
        paths = []
        for th in threads_nums:
            paths.append([])

        for line in lines:
            if self.is_enter(line):
                dire, file, name, typ, thread, max_threads = self.unpack_enter_line(line)
            if self.is_exit(line):
                dire, file, name, typ, thread, max_threads, stime, ctime, wtime = self.unpack_exit_line(line)

            if thread == 1 and max_threads == 1:
                for path in paths:
                    path.append(line)
            else:
                paths[thread-1].append(line)

        return paths



    def unpack_line(self, line):
        line = line.rstrip()
        if self.is_enter(line):
            dire, file, name, typ, thread, max_threads = self.unpack_enter_line(line)
            return dire, file, name, typ, thread, max_threads, 0, 0, 0
        if self.is_exit(line):
            return self.unpack_exit_line(line)  


    def unpack_enter_line(self, line):
        dire, file, name, typ, thread, max_threads = line.split()
        return dire, file, name, typ, int(thread), int(max_threads)

    def unpack_exit_line(self, line):
        dire, file, name, typ, thread, max_threads, stime, ctime, wtime = line.split()
        return dire, file, name, typ, int(thread), int(max_threads), float(stime), float(ctime), float(wtime)

    def get_threads_nums(self, lines):
        threads_nums = set()
        for line in lines:
            threads_nums.add(int(line.split()[4]))
        threads_nums = sorted(threads_nums)
        return threads_nums

    def is_enter(self, line):
        return line.startswith('->')
    def is_exit(self, line):
        return line.startswith('<-')


    def process_chains_sequential(self, stack, chains, line):
        dire, file, name, typ, thread, max_threads, stime, ctime, wtime = self.unpack_line(line)
        if dire == '->':
            stack.append(name)
            stack_string = f"{thread}# {' -> '.join(stack)}"
            if not stack_string in chains:
                chains[stack_string] = {'thread': thread, 'max_threads': max_threads, 'calls':0,
                                        'wtime':0, 'ctime':0, 'self_wtime':0, 'self_ctime':0}
        if dire == '<-':
            if max_threads > 1:
                ctime = stime
            stack_string = f"{thread}# {' -> '.join(stack)}"
            chains[stack_string]['wtime'] += wtime
            chains[stack_string]['ctime'] += ctime
            chains[stack_string]['self_wtime'] += wtime
            chains[stack_string]['self_ctime'] += ctime
            chains[stack_string]['calls'] += 1
            stack.pop()

            if len(stack) > 0:
                stack_string = f"{thread}# {' -> '.join(stack)}"
                chains[stack_string]['self_wtime'] -= wtime
                chains[stack_string]['self_ctime'] -= ctime


    def process_chains_parallel(self, stack, chains, lines, i):
        line = lines[i].rstrip()
        dire, file, name, typ, thread, max_threads, stime, ctime, wtime = self.unpack_line(line)
        sub_stacks = []
        sub_chains = {}
        for n in range(max_threads):
            sub_stacks.append([])

        while max_threads > 1:
            if dire == '->':
                sub_stacks[thread-1].append(name)
                stack_string = f"{thread}# {' -> '.join(sub_stacks[thread-1])}"
                if not stack_string in sub_chains:
                    sub_chains[stack_string] = {'thread': thread, 'max_threads': max_threads, 'calls':0,
                                                'wtime':0, 'ctime':0, 'self_wtime':0, 'self_ctime':0}
            if dire == '<-':
                if max_threads > 1:
                    ctime = stime
                stack_string = f"{thread}# {' -> '.join(sub_stacks[thread-1])}"
                sub_chains[stack_string]['wtime'] += wtime
                sub_chains[stack_string]['ctime'] += ctime
                sub_chains[stack_string]['self_wtime'] += wtime
                sub_chains[stack_string]['self_ctime'] += ctime
                sub_chains[stack_string]['calls'] += 1
                sub_stacks[thread-1].pop()

                stack_string = f"{thread}# {' -> '.join(sub_stacks[thread-1])}"
                if stack_string in sub_chains:
                    sub_chains[stack_string]['self_wtime'] -= wtime
                    sub_chains[stack_string]['self_ctime'] -= ctime

            i += 1
            line = lines[i].rstrip()
            dire, file, name, typ, thread, max_threads, stime, ctime, wtime = self.unpack_line(line)

        i -= 1

        max_wtime = 0
        max_ctime = 0
        stack_string = f"{thread}# {' -> '.join(stack)}"
        for chain, details in sub_chains.items():
            if details['wtime'] > max_wtime:
                max_wtime = details['wtime']
            if details['ctime'] > max_ctime:
                max_ctime = details['ctime']

            i0_ch = chain.index('#') + 2
            i0_st = stack_string.index('#') + 2
            full_string = f"{chain[:i0_ch]}{stack_string[i0_st:]} -> {chain[i0_ch:]}"

            if not full_string in chains:    
                chains[full_string] = details
            else:
                chains[full_string]['wtime'] += details['wtime']
                chains[full_string]['ctime'] += details['ctime']
                chains[full_string]['self_wtime'] += details['self_wtime']
                chains[full_string]['self_ctime'] += details['self_ctime']
                chains[full_string]['calls'] += details['calls']
            del chain

            chains[stack_string]['self_ctime'] -= details['self_ctime']

        chains[stack_string]['self_wtime'] -= max_wtime
        #chains[stack_string]['self_ctime'] -= max_ctime

        return i



    def prepare_chains(self, lines, paths_num):
        file_chains = f"{self.QAWA_OUT}.chains"
        file_chains_rev = f"{self.QAWA_OUT}.chains_rev"
        print(f"Preparing chains...")

        chains = {}
        stack = []


        i = 0
        while i < len(lines):

            line = lines[i].rstrip()
            dire, file, name, typ, thread, max_threads, stime, ctime, wtime = self.unpack_line(line)

            # SEQUENTIAL
            # ----------------------------------------------------------------------
            if max_threads == 1:
                self.process_chains_sequential(stack, chains, line)

            # PARALLEL
            # ----------------------------------------------------------------------
            else:
                i = self.process_chains_parallel(stack, chains, lines, i)


            i += 1

        return chains


    def rollup_chains(self, chains):
        new_chains = {}
        for chain, details in chains.items(): 
            chain_body = chain[chain.index('#')+2:]
            if not chain_body in new_chains:
                new_chains[chain_body] = details
                new_chains[chain_body]['thread'] = ''
            else:
                new_chains[chain_body]['self_wtime'] = max(details['self_wtime'], new_chains[chain_body]['self_wtime'])
                new_chains[chain_body]['wtime'] = max(details['wtime'], new_chains[chain_body]['wtime'])
                new_chains[chain_body]['ctime'] += details['ctime']
                new_chains[chain_body]['self_ctime'] += details['self_ctime']
                new_chains[chain_body]['calls'] += details['calls']
                new_chains[chain_body]['max_threads'] = max(details['max_threads'], new_chains[chain_body]['max_threads'])
        return new_chains



    def save_chains(self, file, chains, sort_key, rollup=False, reverse=False):
        file += '-' + sort_key
        if rollup:
            file += '-roll'
        if reverse:
            file += '-rev'
        with open(file, 'w') as f:
            #f.write(f"{''.join(['-']*(11 + 2 + 11 + 2 + 9 + 2 + 6 + 2 + max_chain_length))}\n")
            chains = dict(sorted(chains.items(), key=lambda item: item[1][sort_key], reverse=True))
            #max_procedure_length = max([len(get_substring_symbol(chain, '->', 'last', 'right'))-2 for chain in chains.keys()])
            #max_chain_length = max([len(get_substring_symbol(chain, '# ', 'first', 'right')) for chain in chains.keys()])
            max_procedure_length = max([len(get_substring_symbol(chain,'->','last','right')) for chain in chains.keys()])
            max_chain_length = max([len(get_substring_symbol(chain,'#','first','right')) for chain in chains.keys()])

            details = f"QAWA CHAINS REPORT (Rollup: {rollup}, Reverse: {reverse}, Sort key: {sort_key})"
            f.write(f"{details}\n")
            f.write(f"File: {file}\n")
            f.write(f"Date: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write(f"{''.join(['-']*len(details))}\n")
            f.write(f"* W-TIME = wall time, C-TIME = CPU time\n")
            f.write(f"* All times expressed in seconds\n")
            f.write(f"{''.join(['-']*len(details))}\n\n")
            #f.write(f"{'':>12s} {'V  DESC.  V':>12s}\n")

            if rollup:
                preheader = f"{'MAX':>{cw[0]}s} | {'TOTAL':>{cw[1]}s} | {'':{cw[2]}s}" + \
                        f" | {'MAX':>{cw[3]}s} | {'TOTAL':>{cw[4]}s} | {'':{cw[5]}s}" + \
                        f" | {'TOTAL':>{cw[6]}s} | {'MAX':>{cw[7]}s} | {''}"
                if reverse:
                    preheader += f"{''.join([' ']*max_procedure_length)} |"
                f.write(f"{preheader}\n") 

            header = f"{'W-TIME':>{cw[0]}s} | {'C-TIME':>{cw[1]}s} | {'C/W':>{cw[2]}s}" + \
                    f" | {'SELF W-TIME':>{cw[3]}s} | {'SELF C-TIME':>{cw[4]}s} | {'C/W':>{cw[5]}s}" + \
                    f" | {'CALLS':>{cw[6]}s} | {'THREADS':>{cw[7]}s}" 

            if reverse:
                header += f" | {'PROCEDURE':{max_procedure_length}s} | {'CALLING CHAIN'}\n"
            else:
                header += f" | {'CHAIN'}\n"
            f.write(header)  

            line = ''
            for c in cw:
                line += f"{''.join(['-']*(c+1))}+-"

            if reverse:
                line += f"{''.join(['-']*(max_procedure_length+1))}+-" 
                line += f"{''.join(['-']*(max_chain_length - max_procedure_length + 1))}\n" 

            else:
                line += f"{''.join(['-']*max_chain_length)}\n"
            f.write(line)


            for chain, details in chains.items():
                #if chain.find('#') > 0:
                #    chain_body = chain[chain.find('#')+2:]
                #else:
                chain_body = get_substring_symbol(chain, '#', 'first', 'right')

                if reverse == True:
                    items = chain_body.split(' -> ')
                    chain_body = ' <- '.join([item for item in items[::-1]])
                    first_arrow = chain_body.find('<-')
                    if first_arrow > 0:
                        chain_body = f"{chain_body[:first_arrow].rstrip():{max_procedure_length}s} | {chain_body[first_arrow:]}"
                    else:
                        chain_body = f"{chain_body.rstrip():{max_procedure_length}s} |"

                threads = f"{details['thread']}/{details['max_threads']}"

                ct_wt = details['ctime'] / details['wtime'] if details['wtime'] > 0 else 1
                self_ct_wt = details['self_ctime'] / details['self_wtime'] if details['self_wtime'] > 0 else 1
                f.write(f"{details['wtime']:{cw[0]}.4f} | {details['ctime']:{cw[1]}.4f} | {ct_wt:{cw[2]}.2f}")
                f.write(f" | {details['self_wtime']:{cw[3]}.4f} | {details['self_ctime']:{cw[4]}.4f} | {self_ct_wt:{cw[5]}.2f}")
                f.write(f" | {details['calls']:{cw[6]}d}") 
                f.write(f" | {threads:>{cw[7]}s} | {chain_body}\n")



    def save_flows(self, lines, paths_num, rollup=False):
        file_flow = f"{self.QAWA_OUT}.flow"
        if rollup:
            file_flow += '_short'
        print(f"Preparing {file_flow}...")

        new_lines = []
        i = 0
        tab = '.   '
        running_tabs = ['#1 '] * paths_num

        while i < len(lines):
            parallel_flows = []
            for th in range(paths_num):
                parallel_flows.append([])

            line = lines[i].rstrip()
            dire, file, name, typ, thread, max_threads, stime, ctime, wtime = self.unpack_line(line)

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
                    dire, file, name, typ, thread, max_threads, stime, ctime, wtime = self.unpack_line(line)


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

        details = f"QAWA FLOW REPORT (Rollup: {rollup})"    
        header = f"{details}\nFile: {file_flow}\nDate: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        header += f"{''.join(['-']*len(details))}\n\n"

        save_file(file_flow,new_lines,header,mode='w') 
