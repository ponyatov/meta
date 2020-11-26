
from metaL import *


class thisModule(rsModule):
    def __init__(self, V=None):
        super().__init__(V)


mod = thisModule()
mod.TITLE = 'message-passing distributed OS'
mod.ABOUT = """
* VM-like guest OS
    * works over any mainstream host OSes
    * embedded Linux preferred
    * standalone mode is possible
* distributed clustering
    * actor programming model
    * message-based programming
    * shared storage
* IoT targeted
    * binary pattern matching
    * realtime message scheduling
"""
mod.d.src.main.top // 'mod forth;'
mod.d.src.main.main // 'forth::forth();'

sync()
