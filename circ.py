
from metaL import *


class thisModule(pyModule):

    external_projects = ['circ', 'SCADA', 'flOwS',
                         'rustpill', 'meteo', 'elixirbook']

    def init_apt(self):
        super().init_apt()
        self.d.apt // 'python3 python3-venv'

    def init_giti(self):
        super().init_giti()
        for s in thisModule.external_projects:
            self.d.giti.bot // f'/{s}/'

    def init_reqs(self):
        super().init_reqs()
        self.d.reqs // 'ply' // 'xxhash'

    def init_mk(self):
        super().init_mk()
        self.d.mk.all.target.flush() // '$(PY)'
        self.d.mk.all.body.flush()
        self.d.mk.obj.flush() //\
            'S += ./do metaL.py'
        for s in thisModule.external_projects + ['bully']:
            self.d.mk.obj // f'S += {s}.py'
        self.d.mk.obj // '#S'
        for s in thisModule.external_projects + ['bully']:
            self.d.mk.all //\
                (S(f'{s}: $(PY) $(S)', pfx='') //
                 f'$(PY) {s}.py')
        self.d.mk.all // '#M'

    def init_vscode_settings(self):
        super().init_vscode_settings()
        self.d.vscode.settings.f11.value = ' make pep '
        self.d.vscode.settings.f12.value = f' clear ; make '
        self.d.vscode.settings.assoc // '"./do": "python",'

    def init_py(self):
        self.init_reqs()
        self.d.py = pyFile('metaL')
        self.d // self.d.py
        #
        self.d.py.imports = Section('imports')
        self.d.py // self.d.py.imports
        for i in ['os', 'sys', 're']:
            self.d.py.imports // Import(i)
        #
        self.c = Section('classtree')
        #
        self.d.py.object = Section('executable graph object')
        self.d.py // self.d.py.object
        self.c.object = Class('Object')
        self.d.py.object // self.c.object
        #
        self.d.py.primitive = Section('primitives')
        self.d.py // self.d.py.primitive
        self.c.primitive = Class('Primitive', [self.c.object])
        self.d.py.primitive // self.c.primitive
        self.c.name = Class('Name', [self.c.primitive])
        self.d.py.primitive // self.c.name
        self.c.string = Class('String', [self.c.primitive])
        self.d.py.primitive // self.c.string
        self.c.number = Class('Number', [self.c.primitive])
        self.d.py.primitive // self.c.number
        self.c.integer = Class('Integer', [self.c.number])
        self.d.py.primitive // self.c.integer
        self.c.hex = Class('Hex', [self.c.integer])
        self.d.py.primitive // self.c.hex


mod = thisModule()
mod.MODULE = 'metaL'
mod.TITLE = 'Homoiconic [meta]programming [L]anguage / [L]ayer'
mod.ABOUT = """
* Discord: https://discord.gg/5CYZdt6
* [book drafts](https://www.notion.so/metalang/Wiki-18ae2c8192bd4b5c8548bf7f56f390d6) en/ru
  * [`metaL` manifest](https://www.notion.so/metalang/metaL-manifest-f7c2e3c9f4494986a620f3a71cf39cff)
  * [Distilled `metaL`](https://www.notion.so/metalang/Distilled-metaL-SICP-chapter-4-237378d385024f899e5a24597da7a19d)
  * [глава 4 Металингвистическая абстракция](https://www.notion.so/metalang/4-eb7dfcf3dbb04e6eb8015337af850aab)
    (частичный перевод с адаптацией)

## Language Ideas Promo

* provide a light environment for **metaprogramming by code generation**
  * `metaL` is a special language for writing programs that write other programs (in Python, Rust,.. as *target languages*)
    * provide abilities to *work with arbitrary source code* (parsing, modification, and synthesis)
      * write your own custom script and experimental languages
* `metaL` is not a programming language
  * `metaL` **is a method of programming** in Python (or any other language you prefer: JS, PHP,...)
    * write scripts which generates your *target code*
* bootstrap the `metaL` core with itself
  * `circ.py` is a (partial) **circular implementation** which generates its code in Python
    * use `meld` to compare and manually sync old and new code versions
* automate new generic project creation with a few lines of Python code
  * run `./do newProject` to open the `newProject.py` in VSCode
  * inherit `thisModule` from one of the predefined project classes
    * Python/Django (web & bootstrap)
    * Erlang/Elixir (SCADA & high-load network services)
    * C/C++/Rust    (embedded devices firmware)
  * add extra scripts which generated some project-specific code
"""

sync()
