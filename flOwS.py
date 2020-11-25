
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
mod.d.readme.rust // """
* [Rust CS196 FA20](https://www.youtube.com/playlist?list=PLddc343N7YqhSPMjlCJa1gRDt4CzjiMYZ)
    * [Welcome to 196! - CS196 FA20](https://www.youtube.com/watch?v=J__JvfNuknU&list=PLddc343N7YqhSPMjlCJa1gRDt4CzjiMYZ&index=1&t=795s)
    * [Rust 1 - Lecture 17 - CS196 FA20](https://www.youtube.com/watch?v=ac7AOtkQMx4)
"""

sync()
