
from metaL import *


class thisModule(exModule):
    def __init__(self, V=None):
        super().__init__(V)


mod = thisModule()
mod.TITLE = 'SCADA-like system in Erlang/Elixir'
mod.ABOUT = """
* (I)IoT-focused
"""

mod.d.readme // '''

***

Несколько дней назад попалась мне вот такая вакансия:

```
IT компания, разработчик B2B решений.

Обязанности:
- Участие в разработке SCADA системы.
- Ваша задача -- развивать отдельное направление развития продукта.

Ждем от Вас:
- опыт web backend от 2х лет
- JS и вёрстка на минималках
- PHP7, PostgreSQL

Будет плюсом:
- опыт работы в АСУТП, автоматизации
- понимание принципов работы SCADA систем, OPC серверов

```

Если кто не знает -- SCADA-система это верхний уровень систем управления
химическим заводом, электростанцией, и т.п. И одна из её важных частей --
обеспечение интерфейса для операторов, диспетчеров на транспорте, дежурных смен.
И от надёжности работы этого интерфейса иногда (?) зависит безопасность. А оно
на PHP. Которое выполняется на сервере, то есть сбои в нём влияют сразу на всех
операторов.

А теперь вспомните, как у вас на десктопе работает браузер, и последние поделки
на Electron. У меня на 2х компах с 6 и 12 Гб (!) ОЗУ периодически приходится
рестартовать сеанс, в особо неудачных случаях перезагружаться с кнопки. Сколько
будет стоить рестарт сервера веб-интерфейса в скаде, в проблемной/аварийной
ситуации? Последние пару лет наблюдается какое-то катастрофическое расползание
wёbдизайнеров на мобильные устройства, и на десктоп.<br>
и SCADA ba-dum-ts

Возникает вопрос: а есть ли у нанимателя "понимание принципов работы SCADA систем"?<br>
что нужны гарантии, резервирование, изоляция памяти процессов, эластичность под
нагрузкой, кластеризация, супервизоры процессов и т.п. И есть ли гарантии, что
разработанную на PHP систему не будут продавать для critical-применений на газовых
станциях, в энергетику, на хим.производства и транспорт?

Так что необходимо использовать хотя бы языки с контролем типов и операций с
памятью, ещё лучше эрланговский подход с полиморфными функциями, которые в
рантайме каждый пакет данных и вызов проверяют на правильность структуры и типа.
Тут даже Java не очень подходит, потому что штатный сборщик мусора надо
настраивать на работу в мягком реалтайме, без заморозки. Точно не Си, нужен
контроль памяти, в многопоточке с гонками и реаллокациями, не напишут без ошибок
многозадачный код те, кто PHP хочет. Возможно Rust, там много чего есть, чтобы
не допускать запоротую память, SCADA это ведь не только статус показывать, там и
управляющие воздействия есть.

Некоторое удивление вызывает отсутствие интереса к стеку языка Erlang, даже с
учётом его специфического синтаксиса, особенно для подобных ответственных
применений, или реализации сервисов в ограниченных ресурсах (встраиваемые
системы). Этот проект является демонстрацией применения виртуальной машины BEAM
и платформы OpenTelecom Platform (OTP) в комплексе с языком Elixir, который
имеет более приятный синтаксис, и веб-фреймворк Phoenix (по мотивам Rails).
'''


mod.d.mix.deps //\
    '{:cowboy, "~> 2.8"},' //\
    '{:ecto, "~> 3.5"},' //\
    '{:json, "~> 1.3"},' //\
    '{:earmark, "~> 1.4"},' //\
    '{:tortoise, "~> 0.9.5"},' //\
    '{:bamboo, "~> 1.6"},' //\
    '#{:mqtt, "~> 0.3.3"},' //\
    '#{:modbus, "~> 0.3.7"},' //\
    '{:exsync, "~> 0.2.4", only: :dev},'

sync()
