#!/usr/bin/env python3

from mainmem import Memory
import math

class SetAssociativeCache(dict):
    '''
    Creates `num_ways`-way set associative cache with `num_sets` sets,
    evicting cache blocks as necessary with a Least-Recently Used policy.
    '''
    def __init__(self, num_sets, num_ways):
        self.cache_write_queries = 0
        self.cache_read_queries = 0
        self.cache_write_misses = 0
        self.cache_read_misses = 0
        self.num_sets = num_sets
        self.num_ways = num_ways
        self.last_use = 0
        self.mm = Memory()  # Main Memory for your simulator
        # create a structure for your cache
        self.cache = {}
        for set_num in range(0, self.num_sets):
            self.cache[set_num] = {}
            for way_num in range(0, self.num_ways):
                self.cache[set_num][way_num] = {}
                self.cache[set_num][way_num]["value"] = []
                for index_num in range(0, int(self.mm.MAIN_MEMORY_WORDS_PER_BLOCK)):
                    self.cache[set_num][way_num]["value"].append(None)
                self.cache[set_num][way_num]["dirty"] = False
                self.cache[set_num][way_num]["empty"] = True
                self.cache[set_num][way_num]["base_addr"] = None
                self.cache[set_num][way_num]["last-use"] = 0

    def calculate_base_index(self, addr):
        assert (addr % 4 == 0), "Misaligned Memory Address"
        addr_offt = ((addr - self.mm.MAIN_MEMORY_START_ADDR) % self.mm.MAIN_MEMORY_BLOCK_SIZE)
        base = addr - addr_offt
        index = math.floor(addr_offt / self.mm.MAIN_MEMORY_WORD_SIZE)
        return base, index

    def base_addr_to_dmc_index(self, base_addr):
        # FIND A SET
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
        return index

    def locate_block(self, set_num, base_addr):
        # 0: look if any of the slots are already that base addr
        for way_num in range(0, self.num_ways):
            if self.cache[set_num][way_num]["base_addr"] == base_addr:   
                self.last_use += 1
                self.cache[set_num][way_num]["last-use"] = self.last_use
                return way_num
        # 1: look for any empty slots, choose that empty slot
        for way_num in range(0, self.num_ways):
            # double check if its already in the cache slot
            if self.cache[set_num][way_num] == None:
                self.last_use += 1
                self.cache[set_num][way_num]["last-use"] = self.last_use
                return way_num
        # 2: if they're all full, yikes!  We'll need to evict stuff
        way_num = self.lru(set_num)
        return way_num

    def lru(self, set_num):
        # let's loop through all of the values and see which was least recently used
        min_value = self.last_use
        return_value = 0
        for way_num in range(0, self.num_ways):
            if self.cache[set_num][way_num]["last-use"] < min_value:
                min_value = self.cache[set_num][way_num]["last-use"]
                return_value = way_num
        self.last_use += 1
        self.cache[set_num][return_value]["last-use"] = self.last_use
        return return_value

    def store_word(self, w_addr, w_data):
        base_addr, index_in_block = self.calculate_base_index(w_addr)
        set_num = self.base_addr_to_dmc_index(base_addr)
        way_num = self.locate_block(set_num, base_addr)

        if self.cache[set_num][way_num]["base_addr"] == base_addr:   
            # is it already loaded in there?  awesome!  just change the single int we need to change
            for index_num in range(0, int(self.mm.MAIN_MEMORY_WORDS_PER_BLOCK)):
                if index_num == index_in_block:
                    self.cache[set_num][way_num]["value"][index_num] = w_data
            self.cache[set_num][way_num]["dirty"] = True
            self.cache[set_num][way_num]["empty"] = False

        elif self.cache[set_num][way_num]["empty"] == True:
            # is the block empty?  ugh, we'll need to read it in before we write it
            block = self.mm.mm_read(base_addr)
            self.cache[set_num][way_num]["value"] = block
            self.cache[set_num][way_num]["empty"] = False
            self.cache[set_num][way_num]["dirty"] = True
            self.cache[set_num][way_num]["base_addr"] = base_addr

            for index_num in range(0, int(self.mm.MAIN_MEMORY_WORDS_PER_BLOCK)):
                if index_num == index_in_block:
                    self.cache[set_num][way_num]["value"][index_num] = w_data
                else:
                    self.cache[set_num][way_num]["value"][index_num] = block[index_num]
            self.cache_write_misses += 1

        else:
            # the block isn't empty, but it's not the correct block line.  we'll need to get rid of it!

            # if the cache is dirty, we must write that value back via store word      
            if self.cache[set_num][way_num]["dirty"]:
                self.mm.mm_write(self.cache[set_num][way_num]["base_addr"], self.cache[set_num][way_num]["value"])

            # now that we've written it back, we'll need to read it in and write it
            block = self.mm.mm_read(base_addr)
            self.cache[set_num][way_num]["value"] = block
            self.cache[set_num][way_num]["empty"] = False
            self.cache[set_num][way_num]["dirty"] = True
            self.cache[set_num][way_num]["base_addr"] = base_addr

            for index_num in range(0, int(self.mm.MAIN_MEMORY_WORDS_PER_BLOCK)):
                if index_num == index_in_block:
                    self.cache[set_num][way_num]["value"][index_num] = w_data
                else:
                    self.cache[set_num][way_num]["value"][index_num] = block[index_num]
            self.cache_write_misses += 1
        self.cache_write_queries += 1
        pass








    def load_word(self, r_addr) -> int:
        base_addr, index_in_block = self.calculate_base_index(r_addr)
        set_num = self.base_addr_to_dmc_index(base_addr)
        way_num = self.locate_block(set_num, base_addr)

        if self.cache[set_num][way_num]["empty"] == True:
            # is the designated cache empty?  oh no! we'll need to load it from memory
            block = self.mm.mm_read(base_addr)
            self.cache[set_num][way_num]["value"] = block
            self.cache[set_num][way_num]["empty"] = False
            self.cache[set_num][way_num]["base_addr"] = base_addr
            return_int = block[index_in_block]
            self.cache_read_misses += 1

        elif self.cache[set_num][way_num]["base_addr"] != base_addr:
            # oh no! the place we're supposed to read from has the wrong stuff in it.
            if self.cache[set_num][way_num]["dirty"]:
                self.cache[set_num][way_num]["dirty"] = False
                self.mm.mm_write(self.cache[set_num][way_num]["base_addr"], self.cache[set_num][way_num]["value"])

            block = self.mm.mm_read(base_addr)
            self.cache[set_num][way_num]["value"] = block
            self.cache[set_num][way_num]["empty"] = False
            self.cache[set_num][way_num]["base_addr"] = base_addr
            return_int = block[index_in_block]
            self.cache_read_misses += 1

        else:
            # all good! we can just load it from the cache
            # get only the word we want, example: word 1 = index 0 = bytes [0:4)
            return_int = self.cache[set_num][way_num]["value"][index_in_block]
            self.cache[set_num][way_num]["base_addr"] = base_addr
        self.cache_read_queries += 1
        return return_int