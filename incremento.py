
from metaL import *


class thisModule(circularModule):
    def __init__(self, V=None):
        super().__init__(V)


mod = thisModule()
mod.TITLE = 'incremental metalanguage implementation'
mod.ABOUT = """
* powered by `metaL`
"""

sync()