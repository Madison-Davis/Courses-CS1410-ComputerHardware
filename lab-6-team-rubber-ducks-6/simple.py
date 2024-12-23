#!/usr/bin/env python3

from mainmem import Memory
import math

class SimpleCache():
    '''
    Useless middle-man that always goes to main memory.
    (I.e., it doesn't cache.)
    '''
    def __init__(self):
        self.cache_write_queries = 0
        self.cache_read_queries = 0
        self.cache_write_misses = 0
        self.cache_read_misses = 0
        self.mm = Memory()  # Main Memory for your simulator
        # don't need to actually initialize a structure for a 
        # cache because this 'SimpleCache' is just an always-miss model
    
    def calculate_base_index(self, addr):
        assert (addr % 4 == 0), "Misaligned Memory Address"
        addr_offt = ((addr - self.mm.MAIN_MEMORY_START_ADDR) % self.mm.MAIN_MEMORY_BLOCK_SIZE)
        base = addr - addr_offt
        index = math.floor(addr_offt / self.mm.MAIN_MEMORY_WORD_SIZE)
        return base, index

    def store_word(self, w_addr, w_data):
        base_addr, index_in_block = self.calculate_base_index(w_addr)
        block = self.mm.mm_read(base_addr)          # pull entire cache line (MAIN_MEMORY_BLOCK_SIZE)
        block[index_in_block] = w_data              # write word in block (i.e., change element of Python list)
        self.mm.mm_write(base_addr, block)          # write block (Python list) back to main memory
        self.cache_write_queries += 1
        self.cache_write_misses  += 1               # always miss

    def load_word(self, r_addr) -> int:
        base_addr, index_in_block = self.calculate_base_index(r_addr)
        block = self.mm.mm_read(base_addr)
        val = block[index_in_block]
        self.cache_read_queries += 1
        self.cache_read_misses  += 1                # always miss
        return val
