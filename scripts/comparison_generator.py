from scripts.strings import *
import os
import re
from scripts.utils import get_separator, read_file, save_file, get_substring_symbol
import datetime

wtime = {'sufix': 'chains-wtime-roll-rev.md', 'type':'wtime', 'line0': 11}
self_wtime = {'sufix': 'chains-self_wtime-roll-rev.md', 'type':'swtime', 'line0': 11}

class Comparison_generator():
    def __init__(self, QAWA_OUTS):
        self.QAWA_OUTS = QAWA_OUTS


    def generate_report(self):
        print("Preparing comparison...")
        
        self.compare_files(wtime)
        self.compare_files(self_wtime)

    #chains-wtime-roll-rev
    #chains-self_wtime-roll-rev

    def compare_files(self, report):
        procedures = {}
        for filename in self.QAWA_OUTS:
            lines = read_file(f"{filename}.{report['sufix']}")
            for line in lines[report['line0']:]:
                wtime, ctime, cw, swtime, sctime, scw, calls, thds, proc, chain = self.unpack_line(line)

                fullname = f"{chain} -> {proc}"
                if not fullname in procedures:
                    procedures[fullname] = {'chain':chain, 'proc':proc}
                procedures[fullname][filename] = {
                                                    'wtime':float(wtime), 
                                                    'ctime':float(ctime), 
                                                    'swtime':float(swtime), 
                                                    'sctime':float(sctime)
                                                    }
        
        self.save_results(self.QAWA_OUTS, report, procedures)
        

    def unpack_line(self, line):
        #line = line.replace(' ', '').strip()
        items = line.strip().split('|')[1:]
        items = [item.strip() for item in items]

        return items


    def save_results(self, files, report, procedures):
        file = f"{files[0]}.{report['sufix']}.COMP.md"
        with open(file, 'w') as f:
            #chains = dict(sorted(chains.items(), key=lambda item: item[1][sort_key], reverse=True))
            max_procedure_length = max([len(get_substring_symbol(proc,'->','last','right')) for proc in procedures.keys()])
            max_chain_length = max([len(proc) for proc in procedures.keys()])
            rollup = True if 'roll' in file else False
            reverse = True if 'rev' in file else False
            sort_key = 'self_wtime' if 'self_wtime' in file else 'wtime'

            title = f"QAWA COMPARISON REPORT"
            if report['type'] == 'wtime':
                title += ' (WALL TIME)'
            if report['type'] == 'swtime':
                title += ' (SELF WALL TIME)'
            #files[0] += ' (REF)'
            filesString = ', '.join(files)
            details = f"Details: rollup={rollup}, reverse={reverse}, sortKey={sort_key}"
            f.write(f"# {title}\n")
            f.write(f"### Files: {filesString}\n")
            f.write(f"#### {details}\n")
            f.write(f"#### File: {file}\n")
            f.write(f"#### Date: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write(f"{''.join(['-']*len(details))}\n")
            f.write(f"* All times expressed in seconds\n")
            f.write(f"{''.join(['-']*len(details))}\n\n")

            header = ''
            for fs in files:
                header += f"| {fs:{11}s} "
            if reverse:
                header += f"| {'PROCEDURE':{max_procedure_length}s} | {'CALLING CHAIN'}\n"
            else:
                header += f"| {'CHAIN'}\n"
            f.write(header) 

            line = '| '
            for fs in files:
                c = max(len(fs), 11)
                line += f"{''.join(['-']*c)}:|-"

            if reverse:
                line += f"{''.join(['-']*(max_procedure_length+1))}|:" 
                line += f"{''.join(['-']*(max_chain_length - max_procedure_length + 1))}\n" 
            else:
                line += f"{''.join(['-']*max_chain_length)}\n"
            f.write(line)

            for proc, info in procedures.items():             
                if reverse == True:
                    items = proc.split(' -> ')
                    proc = ' <- '.join([item for item in items[::-1]])
                    first_arrow = proc.find('<-')
                    if first_arrow > 0:
                        proc = f"{proc[:first_arrow].rstrip():{max_procedure_length}s} | {proc[first_arrow:]}"
                    else:
                        proc = f"{proc.rstrip():{max_procedure_length}s} |"

            #threads = f"{details['thread']}/{details['max_threads']}"
            #proc = proc.replace('<-', ' ← ')
            #proc = proc.replace('->', ' → ')


            for proc, info in procedures.items():
                f.write(f"|")  

                for fs in files:
                    
                    time = 0
                    timeRef = info[files[0]][report['type']] if files[0] in info else 0 
                    if fs in info:
                        time = info[fs][report['type']]
                        if not fs == files[0]:
                            time -= timeRef

                    width = len(fs) if len(fs) > 11 else 11
                    if fs == files[0]:
                        f.write(f" {time:>{width}.4f} |")
                    else:
                        f.write(f" {time:>+{width}.4f} |")

                f.write(f" {info['proc']:>{max_procedure_length}s} | {info['chain']}")
                f.write('\n')

            #     ct_wt = details['ctime'] / details['wtime'] if details['wtime'] > 0 else 1
            #     self_ct_wt = details['self_ctime'] / details['self_wtime'] if details['self_wtime'] > 0 else 1
            #     f.write(f"| {details['wtime']:>{cw[0]}.4f} | {details['ctime']:>{cw[1]}.4f} | {ct_wt:>{cw[2]}.2f}")
            #     f.write(f" | {details['self_wtime']:>{cw[3]}.4f} | {details['self_ctime']:>{cw[4]}.4f} | {self_ct_wt:>{cw[5]}.2f}")
            #     f.write(f" | {details['calls']:>{cw[6]}d}") 
            #     f.write(f" | {threads:>{cw[7]}s} | {chain_body}\n")

