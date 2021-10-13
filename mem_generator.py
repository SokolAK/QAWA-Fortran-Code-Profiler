from strings import *
import os
import re
from utils import *
from line_utils import *
import datetime

#Column widths
cw = [11, 11, 6, 11, 11, 6, 5, 7]

class Mem_generator():
    def __init__(self, QAWA_OUT):
        self.QAWA_OUT = QAWA_OUT


    def generate_report(self):
        print(f"Preparing mem report...")
        filename = self.QAWA_OUT + ".md"
        lines = read_file(self.QAWA_OUT)
        chains = {}
        total_ticks = 0 
        for line in lines:
            sline = line.split()
            min_mem = float(sline[-3])
            max_mem = float(sline[-2])
            ticks = int(sline[-1])
            chain = sline[:-3]
            chain.reverse()
            chain = ' ← '.join(chain)
            chains[chain] = {'diff': max_mem-min_mem, 'min': min_mem, 'max': max_mem, 'ticks': ticks}
            total_ticks += ticks

        with open(filename, 'w') as f:

            chains = dict(sorted(chains.items(), key=lambda item: item[1]['max'], reverse=True))

            title = f"QAWA MEM REPORT"
            # details = f"Details: rollup={rollup}, reverse={reverse}, sortKey={sort_key}"
            f.write(f"# {title}\n")
            # f.write(f"#### {details}\n")
            f.write(f"#### File: {filename}\n")
            f.write(f"#### Date: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write(f"#### Total number of ticks: {total_ticks}\n")

            f.write(f"\n| DIFF [GB] | MAX [GB] | MIN [GB] | TICKS | CHAIN\n")
            f.write(f"|---|---|---|---|---\n")

            for chain, details in chains.items():
                chain_body = get_substring_symbol(chain, '#', 'first', 'right')
                f.write(f"| {details['diff']:3.6f} | {details['max']:3.6f} | {details['min']:3.6f} | {details['ticks']} | {chain}\n")