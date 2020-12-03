
from metaL import *


class thisModule(djModule):
    def __init__(self, V=None):
        super().__init__(V)


mod = thisModule()
mod.TITLE = 'погодный бюллютень'
mod.ABOUT = """
Django-приложение написанное с использованием генеративного метапрограммирования
* универсальная шаблонизация кода
"""
mod.GITHUB = 'https://bitbucket.org/ponyatov'

mod.d.templates.index.mid //\
    (S('<TABLE id="layout">', '</TABLE>'))

sync()
