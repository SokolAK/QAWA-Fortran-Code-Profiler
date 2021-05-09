from strings import *
import os
import re
from utils import *
from line_utils import *
import datetime

#Column widths
cw = [11, 11, 6, 11, 11, 6, 5, 7]

class Chain_generator():
    def __init__(self, QAWA_OUT):
        self.QAWA_OUT = QAWA_OUT
        self.lines = []
        self.units = []

    def generate_report(self):
        lines = read_file(self.QAWA_OUT)
        threads_nums = get_threads_nums(lines)
        paths = prepare_paths(lines, max(threads_nums))
        chains = self.prepare_chains(lines, len(paths))
        self.save_chains(f"{self.QAWA_OUT}.chains", chains, sort_key='self_wtime', reverse=False)
        self.save_chains(f"{self.QAWA_OUT}.chains", chains, sort_key='self_wtime', reverse=True)
        self.save_chains(f"{self.QAWA_OUT}.chains", chains, sort_key='wtime', reverse=False)
        self.save_chains(f"{self.QAWA_OUT}.chains", chains, sort_key='wtime', reverse=True)
        rolled_chains = self.rollup_chains(chains)
        self.save_chains(f"{self.QAWA_OUT}.chains", rolled_chains, sort_key='self_wtime', rollup=True, reverse=True)
        self.save_chains(f"{self.QAWA_OUT}.chains", rolled_chains, sort_key='wtime', rollup=True, reverse=True)


    def process_chains_sequential(self, stack, chains, line):
        dire, file, name, typ, thread, max_threads, stime, ctime, wtime = unpack_line(line)
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
        dire, file, name, typ, thread, max_threads, stime, ctime, wtime = unpack_line(line)
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
            dire, file, name, typ, thread, max_threads, stime, ctime, wtime = unpack_line(line)

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
        #file_chains = f"{self.QAWA_OUT}.chains"
        #file_chains_rev = f"{self.QAWA_OUT}.chains_rev"
        print(f"Preparing chains...")

        chains = {}
        stack = []

        i = 0
        while i < len(lines):

            line = lines[i].rstrip()
            dire, file, name, typ, thread, max_threads, stime, ctime, wtime = unpack_line(line)

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
        file += '.md'
        with open(file, 'w') as f:
            #f.write(f"{''.join(['-']*(11 + 2 + 11 + 2 + 9 + 2 + 6 + 2 + max_chain_length))}\n")
            chains = dict(sorted(chains.items(), key=lambda item: item[1][sort_key], reverse=True))
            #max_procedure_length = max([len(get_substring_symbol(chain, '->', 'last', 'right'))-2 for chain in chains.keys()])
            #max_chain_length = max([len(get_substring_symbol(chain, '# ', 'first', 'right')) for chain in chains.keys()])
            max_procedure_length = max([len(get_substring_symbol(chain,'->','last','right')) for chain in chains.keys()])
            max_chain_length = max([len(get_substring_symbol(chain,'#','first','right')) for chain in chains.keys()])

            title = f"QAWA CHAINS REPORT"
            details = f"Details: rollup={rollup}, reverse={reverse}, sortKey={sort_key}"
            f.write(f"# {title}\n")
            f.write(f"#### {details}\n")
            f.write(f"#### File: {file}\n")
            f.write(f"#### Date: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write(f"{''.join(['-']*len(details))}\n")
            f.write(f"* W-TIME = wall time, C-TIME = CPU time\n")
            f.write(f"* All times expressed in seconds\n")
            f.write(f"{''.join(['-']*len(details))}\n\n")
            #f.write(f"{'':>12s} {'V  DESC.  V':>12s}\n")

            # if rollup:
            #     preheader = f"| {'MAX':>{cw[0]}s} | {'TOTAL':>{cw[1]}s} | {'':{cw[2]}s}" + \
            #             f" | {'MAX':>{cw[3]}s} | {'TOTAL':>{cw[4]}s} | {'':{cw[5]}s}" + \
            #             f" | {'TOTAL':>{cw[6]}s} | {'MAX':>{cw[7]}s} | {''}"
            #     if reverse:
            #         preheader += f"{''.join([' ']*max_procedure_length)} |"
            #     f.write(f"{preheader}\n") 

            header = f"| {'W-TIME':>{cw[0]}s} | {'C-TIME':>{cw[1]}s} | {'C/W':>{cw[2]}s}" + \
                    f" | {'SELF W-TIME':>{cw[3]}s} | {'SELF C-TIME':>{cw[4]}s} | {'C/W':>{cw[5]}s}" + \
                    f" | {'CALLS':>{cw[6]}s} | {'THREADS':>{cw[7]}s}" 

            if reverse:
                header += f" | {'PROCEDURE':{max_procedure_length}s} | {'CALLING CHAIN'}\n"
            else:
                header += f" | {'CHAIN'}\n"
            f.write(header)  

            line = '| '
            for c in cw:
                line += f"{''.join(['-']*(c))}:|-"

            if reverse:
                line += f"{''.join(['-']*(max_procedure_length+1))}|:" 
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
                chain_body = chain_body.replace('<-', '←')
                chain_body = chain_body.replace('->', '→')

                ct_wt = details['ctime'] / details['wtime'] if details['wtime'] > 0 else 1
                self_ct_wt = details['self_ctime'] / details['self_wtime'] if details['self_wtime'] > 0 else 1
                f.write(f"| {details['wtime']:>{cw[0]}.4f} | {details['ctime']:>{cw[1]}.4f} | {ct_wt:>{cw[2]}.2f}")
                f.write(f" | {details['self_wtime']:>{cw[3]}.4f} | {details['self_ctime']:>{cw[4]}.4f} | {self_ct_wt:>{cw[5]}.2f}")
                f.write(f" | {details['calls']:>{cw[6]}d}") 
                f.write(f" | {threads:>{cw[7]}s} | {chain_body}\n")