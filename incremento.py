
from metaL import *


class metaModule(pyModule):
    def init_reqs(self):
        super().init_reqs()
        self.d.reqs // 'ply' // 'xxhash'


class thisModule(metaModule):
    def __init__(self, V=None):
        super().__init__(V)


mod = thisModule()
mod.TITLE = 'incremental metalanguage implementation'
mod.ABOUT = """
* powered by `metaL`
"""

sync()
