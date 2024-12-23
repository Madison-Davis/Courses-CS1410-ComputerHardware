#!/usr/bin/env python3

import argparse
import re

from simple             import SimpleCache
from direct             import DirectMappedCache
from fully              import FullyAssociativeCache
from setassoc           import SetAssociativeCache



# Parse command-line arguments passed to the program
def parse_cli_args():

    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '--num_sets',
        type=int,
        default=8,
        help='the number of sets per cache')
    
    parser.add_argument(
        '--num_ways',
        type=int,
        default=8,
        help='the number of ways per set')

    parser.add_argument(
        '--testfile',
        type=str,
        default='tests/t1.test',
        # required=True,
        help='the test trace file (with read/write addrs and vals) to run')

    parser.add_argument(
        '--cachetype',
        choices=('simple', 'dmc', 'sac', 'fac'),
        default='simple',
        type=str.lower,
        help='the cache structure type (simple, DMC, SAC, or FAC)'
    )

    return parser.parse_args()


class CacheRunner():
    def __init__(self, structure, ways, sets, testfile):
        self.cache_type = structure
        self.testfile = testfile
        self.hit_time = 1
        self.miss_penalty = 10  # default for quantitative modeling
        if (self.cache_type == "simple"):
            self.c = SimpleCache()
            self.descriptor = f"{self.cache_type} cache\n*******************************************"
        elif (self.cache_type == "dmc"):
            self.num_sets = sets
            self.c = DirectMappedCache(self.num_sets)
            self.descriptor = f"{self.cache_type} cache with {self.num_sets} set(s)\n*******************************************"
        elif (self.cache_type == "fac"):
            self.num_ways = ways
            self.c = FullyAssociativeCache(self.num_ways)
            self.descriptor = f"{self.cache_type} cache with {self.num_ways} way(s)\n*******************************************"
        elif (self.cache_type == "sac"):
            self.num_sets = sets
            self.num_ways = ways
            self.c = SetAssociativeCache(self.num_sets, self.num_ways)
            self.descriptor = f"{self.cache_type} cache with {self.num_sets} set(s) and {self.num_ways} way(s)\n*******************************************"

    def run(self):
        with open(self.testfile, "r") as t:
            while(line := t.readline()):
                if matches := re.search(r"^W\s+(0x[0-9a-zA-Z]{4})\s+(-?[0-9]+)\s*$", line):
                    addr = int(matches.group(1), base=16)
                    data = int(matches.group(2))
                    self.c.store_word(addr, data)
                    print(f"{self.cache_type}: Wrote to {'0x{:04x}'.format(addr)}: {data}\n")
                elif matches := re.search(r"^R\s+(0x[0-9a-zA-Z]{4})\s*$", line):
                    addr = int(matches.group(1), base=16)
                    readval = self.c.load_word(addr)
                    print(f"{self.cache_type}: Read from {'0x{:04x}'.format(addr)} the value: {readval}\n")
                else:
                    print("Invalid test format")
        self.print_stats()

    def print_stats(self):
        print("\n\n*******************************************")
        write_hits      = self.c.cache_write_queries - self.c.cache_write_misses
        write_hit_rate  = write_hits/self.c.cache_write_queries * 100 if self.c.cache_write_queries else 0
        read_hits       = self.c.cache_read_queries - self.c.cache_read_misses
        read_hit_rate   = read_hits/self.c.cache_read_queries * 100 if self.c.cache_read_queries else 0
        total_hits      = write_hits + read_hits
        total_queries   = self.c.cache_write_queries + self.c.cache_read_queries
        total_hit_rate  = total_hits / total_queries * 100 if total_queries else 0
        queries         = self.c.cache_write_queries + self.c.cache_read_queries
        misses          = self.c.cache_write_misses + self.c.cache_read_misses
        amat = self.hit_time + (misses/queries)*self.miss_penalty if queries else 0
        print(self.descriptor)
        print(f"Write Hit Rate:	    {'{:.2f}'.format(write_hit_rate)}% ({write_hits}/{self.c.cache_write_queries})")
        print(f"Read Hit Rate:	    {'{:.2f}'.format(read_hit_rate)}% ({read_hits}/{self.c.cache_read_queries})")
        print(f"Total Hit Rate:     {'{:.2f}'.format(total_hit_rate)}% ({total_hits}/{total_queries})")
        print(f"Writes to Main Memory:   {self.c.mm.write_queries}")
        print(f"Reads from Main Memory:  {self.c.mm.read_queries}")
        print(f"Avg. Memory Access Time: {'{:.2f}'.format(amat)} cycles")
        print("*******************************************")


def main():
    cli_args = parse_cli_args()
    CacheRunner(cli_args.cachetype, cli_args.num_ways, cli_args.num_sets, cli_args.testfile).run()


if __name__ == '__main__':
    main()
