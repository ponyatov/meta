#  `metaL`
## Homoiconic [meta]programming [L]anguage / [L]ayer

(c) Dmitry Ponyatov <<dponyatov@gmail.com>> 2020 MIT

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

github: https://github.com/ponyatov/metaL
