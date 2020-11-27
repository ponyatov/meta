
from metaL import *

class thisModule(exModule):
    def __init__(self, V=None):
        super().__init__(V)

mod = thisModule()
mod.TITLE = 'SCADA-like system in Erlang/Elixir'
mod.ABOUT = """
ABOUT
"""

sync()
