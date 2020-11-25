# generative metaprogramming

import os
import sys

import queue
import threading

synq = queue.Queue(maxsize=0x11)


def sync():
    while True:
        try:
            synq.get(block=False).sync()
        except queue.Empty:
            break


class Object:
    def __init__(self, V):
        self.type = self.__class__.__name__.lower()
        self.value = V
        synq.put(self)

    def __format__(self, spec):
        assert not spec
        return f'{self.value}'

    def head(self, prefix=''):
        return f'{prefix}<{self.type}:{self.value}> @{id(self):x}'

    def sync(self):
        print(self.head(prefix='sync: '))


class IO(Object):
    pass


class Dir(IO):
    pass


class File(IO):
    pass


class Module(Object):
    pass


class dirModule(Module):
    def __init__(self, V=None):
        super().__init__(V)
        self.d = Dir(f'self')


class pyModule(dirModule):
    def __init__(self, V=None):
        if not V:
            V = __import__('sys').argv[0]
            V = V.split('/')[-1]
            V = V.split('.')[0]
        super().__init__(V)
