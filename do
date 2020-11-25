#!./bin/python3

import os
import sys
import re

mod = sys.argv[1]
print(f'mod: {mod}')

with open('Makefile') as R:
    F = R.read()
if not re.match(f'{mod}', F):
    with open('Makefile', 'w') as W:
        W.write(F)

try:
    open(f'{mod}.py')
except FileNotFoundError:
    with open(f'{mod}.py', 'w') as W:
        W.write(f'''
from metaL import *

class thisModule(dirModule):
    def __init__(self, V=None):
        super().__init__(V)

mod = thisModule()
mod.TITLE = '{mod}'
mod.ABOUT = """
ABOUT
"""

sync()
''')
    os.system(f'code {mod}.py')
