#!/usr/bin/env python3

from mainmem import Memory
import math


class DirectMappedCache(dict):
    '''
    Maps `num_sets` cache blocks into deterministic locations in a direct mapped 
    cache via a hash function on the tag (in our case the whole address, except 
    we ignore the bits that offset into a given block).
    '''

    def __init__(self, num_sets):
        self.cache_write_queries = 0
        self.cache_read_queries = 0
        self.cache_write_misses = 0
        self.cache_read_misses = 0
        self.num_sets = num_sets
        self.mm = Memory()  # Main Memory for your simulator
        # create a structure for your cache
        self.cache = {}
        for set_num in range(0, num_sets):
            self.cache[set_num] = {}
            self.cache[set_num]["value"] = []
            for index_num in range(0, int(self.mm.MAIN_MEMORY_WORDS_PER_BLOCK)):
                self.cache[set_num]["value"].append(None)
            self.cache[set_num]["dirty"] = False
            self.cache[set_num]["base_addr"] = None
            self.cache[set_num]["empty"] = True

    def calculate_base_index(self, addr):
        assert (addr % 4 == 0), "Misaligned Memory Address"
        addr_offt = ((addr - self.mm.MAIN_MEMORY_START_ADDR) %
                     self.mm.MAIN_MEMORY_BLOCK_SIZE)
        base = addr - addr_offt
        index = math.floor(addr_offt / self.mm.MAIN_MEMORY_WORD_SIZE)
        return base, index

    def base_addr_to_dmc_index(self, base_addr):
        # calculate num of bits needed to index things (based on num_sets)
        num_bits_needed = len(str(bin(self.num_sets)))
        # grab ls bits of the base_addr based on the number of bits needed
        # then, convert it to decimal
        # 0, 32, 64, ...
        index = 0
        counter = 0
        if (int(base_addr) % 32 == 0):  # make sure aligned to 0, 32, 64...
            while ((32*counter) - int(base_addr) != 0):
                counter += 1
                if index == self.num_sets - 1:
                    index = 0
                else:
                    index += 1
        # pass
        return index

    def store_word(self, w_addr, w_data):
        base_addr, index_in_block = self.calculate_base_index(w_addr)
        set_num = self.base_addr_to_dmc_index(base_addr)

        if self.cache[set_num]["base_addr"] == base_addr:   
            # is it already loaded in there?  awesome!  just change the single int we need to change
            for index_num in range(0, int(self.mm.MAIN_MEMORY_WORDS_PER_BLOCK)):
                if index_num == index_in_block:
                    self.cache[set_num]["value"][index_num] = w_data
            self.cache[set_num]["dirty"] = True
            self.cache[set_num]["empty"] = False

        elif self.cache[set_num]["empty"] == True:
            # is the block empty?  ugh, we'll need to read it in before we write it
            block = self.mm.mm_read(base_addr)
            self.cache[set_num]["value"] = block
            self.cache[set_num]["empty"] = False
            self.cache[set_num]["dirty"] = True
            self.cache[set_num]["base_addr"] = base_addr

            for index_num in range(0, int(self.mm.MAIN_MEMORY_WORDS_PER_BLOCK)):
                if index_num == index_in_block:
                    self.cache[set_num]["value"][index_num] = w_data
                else:
                    self.cache[set_num]["value"][index_num] = block[index_num]
            self.cache_write_misses += 1

        else:
            # the block isn't empty, but it's not the correct block line.  we'll need to get rid of it!

            # if the cache is dirty, we must write that value back via store word      
            if self.cache[set_num]["dirty"]:
                self.mm.mm_write(self.cache[set_num]["base_addr"], self.cache[set_num]["value"])

            # now that we've written it back, we'll need to read it in and write it
            block = self.mm.mm_read(base_addr)
            self.cache[set_num]["value"] = block
            self.cache[set_num]["empty"] = False
            self.cache[set_num]["dirty"] = True
            self.cache[set_num]["base_addr"] = base_addr

            for index_num in range(0, int(self.mm.MAIN_MEMORY_WORDS_PER_BLOCK)):
                if index_num == index_in_block:
                    self.cache[set_num]["value"][index_num] = w_data
                else:
                    self.cache[set_num]["value"][index_num] = block[index_num]
            self.cache_write_misses += 1
        self.cache_write_queries += 1
        pass

    def load_word(self, r_addr) -> int:
        base_addr, index_in_block = self.calculate_base_index(r_addr)
        set_num = self.base_addr_to_dmc_index(base_addr)

        if self.cache[set_num]["empty"] == True:
            # is the designated cache empty?  oh no! we'll need to load it from memory
            block = self.mm.mm_read(base_addr)
            self.cache[set_num]["value"] = block
            self.cache[set_num]["empty"] = False
            self.cache[set_num]["base_addr"] = base_addr
            return_int = block[index_in_block]
            self.cache_read_misses += 1

        elif self.cache[set_num]["base_addr"] != base_addr:
            # oh no! the place we're supposed to read from has the wrong stuff in it.
            if self.cache[set_num]["dirty"]:
                self.cache[set_num]["dirty"] = False
                self.mm.mm_write(self.cache[set_num]["base_addr"], self.cache[set_num]["value"])

            block = self.mm.mm_read(base_addr)
            self.cache[set_num]["value"] = block
            self.cache[set_num]["empty"] = False
            self.cache[set_num]["base_addr"] = base_addr
            return_int = block[index_in_block]
            self.cache_read_misses += 1

        else:
            # all good! we can just load it from the cache
            # get only the word we want, example: word 1 = index 0 = bytes [0:4)
            return_int = self.cache[set_num]["value"][index_in_block]
            self.cache[set_num]["base_addr"] = base_addr
        self.cache_read_queries += 1
        return return_int
