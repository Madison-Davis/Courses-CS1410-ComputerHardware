#!/usr/bin/env python3

class Memory(dict):
    '''
    Reads memory from a mem.data file.  
    Associates each line's data with an address in a dictionary.
    Read and write from/to this dictionary.
    '''

    def __init__(self):
        self.MAIN_MEMORY_SIZE            = 65536
        self.MAIN_MEMORY_SIZE_LN         = 16
        self.MAIN_MEMORY_START_ADDR      = 0x0000
        self.MAIN_MEMORY_BLOCK_SIZE      = 32
        self.MAIN_MEMORY_BLOCK_SIZE_LN   = 5
        self.MAIN_MEMORY_INIT_FILE       = "./mm_init.data"
        self.MAIN_MEMORY_WORD_SIZE       = 4 # bytes (in accordance with RISC-V)
        self.MAIN_MEMORY_WORDS_PER_BLOCK = self.MAIN_MEMORY_BLOCK_SIZE / self.MAIN_MEMORY_WORD_SIZE

        self.write_queries  = 0
        self.read_queries   = 0
        self[0]             = []    # initialize dictionary value to be a list

        with open(self.MAIN_MEMORY_INIT_FILE, mode="rb") as mem_init:
            i = 0   # index simulates an integer's "address" in main memory
            j = 0   # indexes in a block
            while (byte := mem_init.read(4)):
                # insert into dictionary
                # i is BLOCK_ALIGNED address which indexes a whole block (8 ints)
                # j is an index to the relevant word in a block
                # { 0 : [int0, int1, int2, ... , int7], 32 : [int0, ...], 64 : [...], ...}

                self[i].append(int.from_bytes(byte, byteorder="little", signed=True))
                j += 1
                if j >= self.MAIN_MEMORY_WORDS_PER_BLOCK:
                    j = 0
                    i += self.MAIN_MEMORY_BLOCK_SIZE
                    self[i] = []    # initialize list at next index
    
    def mm_read(self, addr) -> list:
        if addr in self:
            self.read_queries += 1
            print(f"MM:  Read {self.MAIN_MEMORY_BLOCK_SIZE} bytes at {'0x{:04x}'.format(addr)}")
            return self[addr]   # returns a list (a "cache block" of sorts)
        else:
            raise Exception("INVALID MAIN MEMORY ADDRESS")

    def mm_write(self, addr, block):
        assert len(block) == self.MAIN_MEMORY_WORDS_PER_BLOCK, "MAINMEM ERROR: wrong sized block!"
        if addr in self:
            self.write_queries += 1
            print(f"MM:  Wrote {self.MAIN_MEMORY_BLOCK_SIZE} bytes at {'0x{:04x}'.format(addr)}")
            self[addr] = block
        else:
            raise Exception("INVALID MAIN MEMORY ADDRESS")
