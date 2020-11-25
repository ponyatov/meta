import os,sys

class Object:
    def __init__(self,V):
        self.type = self.__class__.__name__.lower()
        self.value =V

class Module(Object): pass

class pyModule(Module):
    def __init__(self,V=None):
        if not V:
            V = __import__('sys').argv[0]
            V = V.split('/')[-1]
            V = V.split('.')[0]
        super().__init__(V)
