
from metaL import *


class thisModule(pyModule):
    def init_vscode_settings(self):
        super().init_vscode_settings()
        self.d.vscode.settings.f11.value = ' make pep '
        self.d.vscode.settings.f12.value = f' clear ; make {self} '
        self.d.vscode.settings.assoc // './do": "python",'


mod = thisModule()
mod.MODULE = 'metaL'
mod.TITLE = 'Homoiconic [meta]programming [L]anguage / [L]ayer'
mod.ABOUT = """
* `github`: https://github.com/ponyatov/metaL
* Discord: https://discord.gg/5CYZdt6
* [book drafts](https://www.notion.so/metalang/Wiki-18ae2c8192bd4b5c8548bf7f56f390d6) en/ru
  * [`metaL` manifest](https://www.notion.so/metalang/metaL-manifest-f7c2e3c9f4494986a620f3a71cf39cff)
  * [Distilled `metaL`](https://www.notion.so/metalang/Distilled-metaL-SICP-chapter-4-237378d385024f899e5a24597da7a19d)
  * [глава 4 Металингвистическая абстракция](https://www.notion.so/metalang/4-eb7dfcf3dbb04e6eb8015337af850aab)
    (частичный перевод с адаптацией)

## Language Ideas Promo

* provide a light environment for **metaprogramming by code generation**
  * `metaL` is a special language for writing programs that write other programs (in C & Python as *target languages*)

## `metaL` is not a programming language

`metaL` **is a method of programming** in Python (or any other language you prefer: JS, PHP,...)

"""

mod.d.giti.bot //\
    '/circ/' //\
    '/SCADA/'

sync()
