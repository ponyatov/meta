
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
    (DIV(id="trhead", clazz='row') //
        (DIV(id="logo", clazz='col-2') //
         (A(href="/admin/") // IMG(src="/static/logo.png"))
         ) //
        (DIV(id="tdhead", clazz='col-8') //
         P('Министерство природных ресурсов и экологии Российской Федерации') //
         P('Федеральная служба по гидрометеорологии и мониторингу окружающей среды') //
         P('Федеральное государственное бюджетное учреждение') //
         P('Приволжское управление по гидрометеорологии<br>и мониторингу окружающей среды') //
         P('гидрометеорологический центр') //
         '') //
        (DIV(id="shortdate", clazz='col-2') //
         '{{date}}<br>{{time}}')
     )

user =\
    (TD(id="user") //
        P('исполнитель: {{user.name}}') //
        P('e-mail: &LT;<A href="mailto:{{user.email}}">{{user.email}}</A>&GT;') //
        P('телефон: {{user.phone}}') //
        P('<HR>{{loc}}') //
     '')

version =\
    (TD(id="version") //
     '<H1>погодный бюллютень</H1>' //
     '')

address =\
    (TD(id="address") //
     P('443125 г.Самара') //
     P('ул.Ново-Садовая, 325') //
     P('e-mail: &LT;<A href="mailto:cks@pogoda-sv.ru">cks@pogoda-sv.ru</A>&GT;') //
     P('телефон +7 846 994 3678') //
     P('+7 846 952 9909') //
     '')

trmaker = \
    (TR(id="trmaker") //
        user //
        version //
        address //
     '')

mod.d.templates.index.mid //\
    (DIV(clazz='container-fluid') //
        trhead //
     (TABLE(id='layout') //
        trmaker //
      '')
     )

mod.d.dj.views.index.context //\
    "'date':time.strftime('%d.%m.%y')," //\
    "'time':time.strftime('%H:%M'),"

mod.d.dj.forms.mid //\
    'import datetime as dt' //\
    (Class(f'{mod}Form', ['forms.Form']) //
     (S('date = forms.DateField(', ')') //
      'initial = dt.date.today(),' //
      (S('widget= forms.SelectDateWidget(', ')')//'') //
      ''))

sync()
