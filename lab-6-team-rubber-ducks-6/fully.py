#!/usr/bin/env python3

from mainmem import Memory
import math


class FullyAssociativeCache(list):
    '''
    Fits `num_ways` cache blocks into various locations in a fully associative
    cache, evicting as necessary with a Least-Recently Used policy.
    '''

    def __init__(self, num_ways):
        self.cache_write_queries = 0
        self.cache_read_queries = 0
        self.cache_write_misses = 0
        self.cache_read_misses = 0
        self.num_ways = num_ways
        self.last_use = 0 # for LRU policy
        self.mm = Memory()  # Main Memory for your simulator
        # create a structure for your cache
        self.cache = {}
        for way_num in range(0, self.num_ways):
            self.cache[way_num] = {}
            self.cache[way_num]["value"] = []
            for index_num in range(0, int(self.mm.MAIN_MEMORY_WORDS_PER_BLOCK)):
                self.cache[way_num]["value"].append(None)
            self.cache[way_num]["dirty"] = False
            self.cache[way_num]["base_addr"] = None
            self.cache[way_num]["empty"] = True
            self.cache[way_num]["last-use"] = 0

    def calculate_base_index(self, addr):
        assert (addr % 4 == 0), "Misaligned Memory Address"
        addr_offt = ((addr - self.mm.MAIN_MEMORY_START_ADDR) %
                     self.mm.MAIN_MEMORY_BLOCK_SIZE)
        base = addr - addr_offt
        index = math.floor(addr_offt / self.mm.MAIN_MEMORY_WORD_SIZE)
        return base, index

    def locate_block(self, base_addr):
        # 0: look if any of the slots are already that base addr
        for way_num in range(0, self.num_ways):
            if self.cache[way_num]["base_addr"] == base_addr:   
                self.last_use += 1
                self.cache[way_num]["last-use"] = self.last_use
                return way_num
        # 1: look for any empty slots, choose that empty slot
        for way_num in range(0, self.num_ways):
            if self.cache[way_num] == None:
                self.last_use += 1
                self.cache[way_num]["last-use"] = self.last_use
                return way_num
        # 2: if they're all full, yikes!  We'll need to evict stuff
        way_num = self.lru()
        return way_num

    def lru(self):
        # let's loop through all of the values and see which was least recently used
        min_value = self.last_use
        return_value = 0
        for way_num in range(0, self.num_ways):
            if self.cache[way_num]["last-use"] < min_value:
                min_value = self.cache[way_num]["last-use"]
                return_value = way_num
        self.last_use += 1
        self.cache[return_value]["last-use"] = self.last_use
        return return_value

    def store_word(self, w_addr, w_data):
        base_addr, index_in_block = self.calculate_base_index(w_addr)
        way_num = self.locate_block(base_addr)
        if self.cache[way_num]["base_addr"] == base_addr:   
            # is it already loaded in there?  awesome!  just change the single int we need to change
            for index_num in range(0, int(self.mm.MAIN_MEMORY_WORDS_PER_BLOCK)):
                if index_num == index_in_block:
                    self.cache[way_num]["value"][index_num] = w_data
            self.cache[way_num]["dirty"] = True
            self.cache[way_num]["empty"] = False

        elif self.cache[way_num]["empty"] == True:
            # is the block empty?  ugh, we'll need to read it in before we write it
            block = self.mm.mm_read(base_addr)
            self.cache[way_num]["value"] = block
            self.cache[way_num]["empty"] = False
            self.cache[way_num]["dirty"] = True
            self.cache[way_num]["base_addr"] = base_addr

            for index_num in range(0, int(self.mm.MAIN_MEMORY_WORDS_PER_BLOCK)):
                if index_num == index_in_block:
                    self.cache[way_num]["value"][index_num] = w_data
                else:
                    self.cache[way_num]["value"][index_num] = block[index_num]
            self.cache_write_misses += 1

        else:
            # the block isn't empty, but it's not the correct block line.  we'll need to get rid of it!

            # if the cache is dirty, we must write that value back via store word      
            if self.cache[way_num]["dirty"]:
                self.mm.mm_write(self.cache[way_num]["base_addr"], self.cache[way_num]["value"])

            # now that we've written it back, we'll need to read it in and write it
            block = self.mm.mm_read(base_addr)
            self.cache[way_num]["value"] = block
            self.cache[way_num]["empty"] = False
            self.cache[way_num]["dirty"] = True
            self.cache[way_num]["base_addr"] = base_addr

            for index_num in range(0, int(self.mm.MAIN_MEMORY_WORDS_PER_BLOCK)):
                if index_num == index_in_block:
                    self.cache[way_num]["value"][index_num] = w_data
                else:
                    self.cache[way_num]["value"][index_num] = block[index_num]
            self.cache_write_misses += 1
        self.cache_write_queries += 1
        pass
















    def load_word(self, r_addr) -> int:
        base_addr, index_in_block = self.calculate_base_index(r_addr)
        way_num = self.locate_block(base_addr)

        if self.cache[way_num]["empty"] == True:
            # is the designated cache empty?  oh no! we'll need to load it from memory
            block = self.mm.mm_read(base_addr)
            self.cache[way_num]["value"] = block
            self.cache[way_num]["empty"] = False
            self.cache[way_num]["base_addr"] = base_addr
            return_int = block[index_in_block]
            self.cache_read_misses += 1

        elif self.cache[way_num]["base_addr"] != base_addr:
            # oh no! the place we're supposed to read from has the wrong stuff in it.
            if self.cache[way_num]["dirty"]:
                self.cache[way_num]["dirty"] = False
                self.mm.mm_write(self.cache[way_num]["base_addr"], self.cache[way_num]["value"])

            block = self.mm.mm_read(base_addr)
            self.cache[way_num]["value"] = block
            self.cache[way_num]["empty"] = False
            self.cache[way_num]["base_addr"] = base_addr
            return_int = block[index_in_block]
            self.cache_read_misses += 1

        else:
            # all good! we can just load it from the cache
            # get only the word we want, example: word 1 = index 0 = bytes [0:4)
            return_int = self.cache[way_num]["value"][index_in_block]
            self.cache[way_num]["base_addr"] = base_addr
        self.cache_read_queries += 1
        return return_int