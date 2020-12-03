
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


mod.d.static.css //\
"""
* { background:#222;}
table #layout { width: 100%; }
table,tr,td { border: 1pt solid yellow; }
"""

mod.d.templates.index.mid //\
    (TABLE(id='layout') //
        (TR(id="tablehead") //
            (TD() //
                (TABLE(id="tablehead") //
                    (TR() //
                        (TD(id="logo") //
                            (A(href="/admin/") // IMG(src="/static/logo.png"))
                         ) //\
                         (TD(id="tinyhead")//\
                            P('Министерство природных ресурсов и экологии Российской Федерации')//\
                            P('Федеральная служба по гидрометеорологии и мониторингу окружающей среды')//\
                            P('Федеральное государственное бюджетное учреждение')//\
                            P('Приволжское управление по гидрометеорологии<br>и мониторингу окружающей среды')//\
                            P('гидрометеорологический центр')//\
                         '')

                     )
                 )
             )
         )
     )

sync()
