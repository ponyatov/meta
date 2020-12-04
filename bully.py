
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
table           { width: 100%;                            }
table *         { padding: 4px;                           }
table #tdhead p { margin-bottom:0; text-align: center;    }
table *         { border: 1pt solid yellow;               }
tr              { border: 1pt solid blue;                 }
   td           { border: 1pt solid green;                }
#shortdate      { text-align: right; vertical-align: top; }     
""" //\
    (S('@media print {', '}')//"""
""")

trhead = \
    (TR(id="trhead") //
     (TD() //
      (TABLE(id="trhead") //
       (TR() //
        (TD(id="logo") //
         (A(href="/admin/") // IMG(src="/static/logo.png"))
         ) //
        (TD(id="tdhead") //
         P('Министерство природных ресурсов и экологии Российской Федерации') //
         P('Федеральная служба по гидрометеорологии и мониторингу окружающей среды') //
         P('Федеральное государственное бюджетное учреждение') //
         P('Приволжское управление по гидрометеорологии<br>и мониторингу окружающей среды') //
         P('гидрометеорологический центр') //
         '') //
        (TD(id="shortdate") // 'shortdate')
        )
       )
      )
     )

trmaker = \
    (TR(id="trmaker") //
     '')

mod.d.templates.index.mid //\
    (TABLE(id='layout') //
        trhead //
        trmaker
     )

sync()
