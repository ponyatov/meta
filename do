#!./bin/python3

import os
import sys
import re

mod = sys.argv[1]
print(f'mod: {mod}')


with open('Makefile') as R:
    F = R.read()
if not re.findall(f'{mod}.py', F):
    with open('Makefile', 'w') as W:
        F = re.sub(
            r'#S',
            f'S += {mod}.py\n#S',
            F)
        F = re.sub(
            r'#M',
            f'\n{mod}: $(PY) $(S)\n\t$(PY) {mod}.py\n#M',
            F)
        W.write(F)


with open('.vscode/settings.json') as R:
    F = R.read()
with open('.vscode/settings.json', 'w') as W:
    F = re.sub(
        r'(\\u000D)[^\\]*(\\u000D)',
        f'\\1 clear ; make {mod} \\2',
        F)
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
