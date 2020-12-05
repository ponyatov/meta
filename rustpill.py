
from metaL import *


class thisModule(rsemModule):
    def __init__(self, V=None):
        super().__init__(V)


mod = thisModule()
mod.TITLE = 'embedded Rust sample for stm32f130 blue pill'
mod.ABOUT = """"""

sync()
