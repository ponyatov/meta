# generative metaprogramming

import os
import sys
import re

import queue

synqueue = queue.Queue(maxsize=0x1111)


def sync():
    while True:
        try:
            synqueue.get(block=False).sync()
        except queue.Empty:
            break


class Object:

    def __init__(self, V):
        self.type = self.__class__.__name__.lower()
        self.value = V
        self.slot = {}
        self.nest = []
        #
        self.synq()

    def __format__(self, spec):
        assert not spec
        return f'{self.value}'

    def head(self, prefix=''):
        return f'{prefix}<{self.type}:{self.value}> @{id(self):x}'

    def synq(self):
        def s(): synqueue.put(self, block=False)
        try:
            s()
        except queue.Full:
            sync()
            s()

    def sync(self):
        print(self.head(prefix='sync: '))

    def __floordiv__(self, that):
        assert isinstance(that, Object)
        self.nest.append(that)
        self.synq()


class IO(Object):
    pass


class Dir(IO):

    def __init__(self, V):
        assert re.match(r'[a-z]+', V)
        super().__init__(V)
        self.path = V

    def sync(self):
        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass
        super().sync()

    def __floordiv__(self, that):
        assert isinstance(that, File)
        that.path = f'{self.path}/{that.value}'
        return super().__floordiv__(that)


class File(IO):

    def __init__(self, V, ext='', tab=' '*4, comment='#'):
        super().__init__(f'{V}{ext}')
        self.ext = ext
        self.tab = tab
        self.comment = comment
        self.commend = ''

    def sync(self):
        with open(self.path, 'w') as W:
            W.write(self.head())


class mkFile(File):
    def __init__(self, V='Makefile', ext='', tab='\t', comment='#'):
        super().__init__(V, ext, tab, comment)


class Module(Object):
    pass


class dirModule(Module):
    def __init__(self, V=None):
        if not V:
            V = __import__('sys').argv[0]
            V = V.split('/')[-1]
            V = V.split('.')[0]
        super().__init__(V)
        self.d = Dir(f'{self}')
        self.init_mk()
        self.init_apt()
        self.init_giti()

    def init_mk(self):
        self.d.mk = mkFile()
        self.d // self.d.mk

    def init_apt(self):
        pass

    def init_giti(self):
        pass


class pyModule(dirModule):
    def __init__(self, V=None):
        super().__init__(V)
