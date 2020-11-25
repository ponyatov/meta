
from metaL import *


class thisModule(dirModule):
    def __init__(self, V=None):
        super().__init__(V)


mod = thisModule()
mod.TITLE = 'ruts'
mod.ABOUT = """
ABOUT
"""

sync()
