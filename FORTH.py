
from metaL import *


class thisModule(cppModule):
    def __init__(self, V=None):
        super().__init__(V)


mod = thisModule()
mod.TITLE = 'primitive CLI/script engine'
mod.ABOUT = """
"""

vm = cFile('vm')
mod.d.src // vm

compiler = cppFile('compiler')
mod.d.src // compiler

lex = lexFile('lexer')
mod.d.src // lex

yacc = yaccFile('parser')
mod.d.src // yacc

frt = File('FORTH', ext='.frt', comment='\\')
mod.d.src // frt
frt //\
    f'\\ {mod} : {mod.TITLE}' //\
    f'\\ (c) {mod.AUTHOR} <{mod.EMAIL}> {mod.YEAR} {mod.LICENSE}' // ''

mod.d.mk.obj //\
    'BINS += $(BIN)/vm $(BIN)/compiler' //\
    'BC   += $(TMP)/$(MODULE).bc'
mod.d.mk.all.target // '$(BINS) $(BC)'
mod.d.mk.all.body //\
    '$(BIN)/vm $(TMP)/FORTH.bc'

mod.d.vscode.extensions // '"fttx.language-forth",'

mod.d.mk.rule //\
    (S('$(TMP)/%.bc: $(BIN)/compiler $(SRC)/%.4th')//'$^ $@')

vm //\
    (S('int main(int argc, char* argv[]) {', '}')//'return 0;')

compiler //\
    (S('int main(int argc, char* argv[]) {', '}')//'return 0;')

sync()
