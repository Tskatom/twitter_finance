#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: ts=4 sts=4 sw=4 tw=79 sta et
"""%prog
"""

import sys
import os
import json
import multiprocessing as mp
from collections import defaultdict


def spawn(f, verbose_level=0):
    def fun(pipe, verbose_level=verbose_level):
        output_q, input_q = pipe
        output_q.close()
        pname = "%s (%d)" % (mp.current_process().name, os.getpid())
        if verbose_level > 1:
            sys.stderr.write(pname + " started\n")

            i = 0
            while True:
                x = input_q.recv()
                if x is None:
                    break
                f(*x)
                i += 1
        else:
            while True:
                x = input_q.recv()
                if x is None:
                    break
                f(*x)

        MapReduce.IQUEUE.put(('__map_reduce_mp_event__', 'worker_ended'))
        if verbose_level > 1:
            sys.stderr.write("%s: ending (%d items processed)\n" % (pname, i))
    return fun


class MapReduce:
    IQUEUE = mp.Queue()

    MAP_PHASE = 0
    REDUCE_PHASE = 1

    def __init__(self, num_workers=None, verbose_level=0):
        self.verbose_level = verbose_level
        self.intermediate_values = defaultdict(list)
        self.result = []
        cpu_count = mp.cpu_count()
        if num_workers and num_workers <= cpu_count:
            self.num_workers = num_workers
        else:
            self.num_workers = cpu_count

    def emit_intermediate(self, key, value):
        MapReduce.IQUEUE.put( (key, value) )

    def emit(self, value):
        MapReduce.IQUEUE.put(value)

    def _doPar(self, func, iterable, phase=MAP_PHASE):
        """It applies the given function to each item in the iterable by spawing
        a number of worker processes. Each item should be tuple containing the
        arguments for the function."""
        name = "Mapper"
        if phase == MapReduce.REDUCE_PHASE:
            name = "Reducer"
        if self.verbose_level > 0:
            sys.stderr.write("Master[%s phase]: starting\n" % name)
        pipes = [mp.Pipe() for _ in range(self.num_workers)]
        proc = [mp.Process(target=spawn(func), name=name, args=(q, self.verbose_level,)) for q in pipes]
        for p in proc:
            p.daemon = True
            p.start()
        for output_p, input_p in pipes:
            input_p.close() # we don't need to read from the pipes
        qi = 0
        for item in iterable:
            pipes[qi][0].send(item)
            qi = (qi+1) % self.num_workers
        for q,_ in pipes:
            q.send(None)  # add termination tokens
            q.close()
        if self.verbose_level > 0:
            sys.stderr.write("Master[%s phase]: feeding workers ended..\n" % name)
        active_workers = self.num_workers
        if phase == MapReduce.MAP_PHASE:
            # Start gathering the intermediate results:
            while active_workers > 0:
                key, value = MapReduce.IQUEUE.get()
                if key == '__map_reduce_mp_event__' and value == 'worker_ended':
                    active_workers -= 1
                else:
                    self.intermediate_values[key].append(value)
        else:
            # Reduce phase: gather final results:
            while active_workers > 0:
                value = MapReduce.IQUEUE.get()
                if isinstance(value, tuple) and value[0] == '__map_reduce_mp_event__' and value[1] == 'worker_ended':
                    active_workers -= 1
                else:
                    self.result.append(value)
        if self.verbose_level > 0:
            sys.stderr.write("Master[%s phase]: gathering results ended..\n" % name)
        for p in proc:
            p.join()

    def execute(self, data, mapper, reducer):
        self._doPar(mapper, ((d,) for d in data), phase=MapReduce.MAP_PHASE)
        self._doPar(reducer, self.intermediate_values.items(), phase=MapReduce.REDUCE_PHASE)
        jenc = json.JSONEncoder()
        for item in self.result:
            yield item
