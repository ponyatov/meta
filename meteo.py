
from metaL import *


class thisModule(exModule):
    def __init__(self, V=None):
        super().__init__(V)
        exModule.mixin_web(self)


mod = thisModule()
mod.TITLE = 'ФГБУ "Приволжское УГМС"'
mod.ABOUT = """
* http://pogoda-sv.ru

вариант реализации корпоративного сайта на платформе Erlang/Elixir
"""
mod.GITHUB = 'https://bitbucket.org/ponyatov'

sync()
