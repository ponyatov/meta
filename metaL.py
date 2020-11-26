# generative metaprogramming

import os
import sys
import re

import queue

synqueue = queue.Queue(maxsize=0x1111)


def sync():
    while True:
        try:
            synqueue.get(block=False).sync()
        except queue.Empty:
            break


class Object:

    def __init__(self, V):
        self.type = self.__class__.__name__.lower()
        self.value = V
        self.slot = {}
        self.nest = []
        #
        self.synced = False
        self.synq()

    def __format__(self, spec):
        if spec == '':
            return f'{self.value}'
        if spec == 'l':
            return f'{self.value.lower()}'
        raise TypeError(spec)

    def keys(self):
        return sorted(self.slot.keys())

    def test(self): return self.dump(test=True)

    def dump(self, depth=0, prefix='', tab='\t', test=False):
        ret = self.pad(depth, tab)
        ret += self.head(prefix, test)
        for i in self.keys():
            ret += self[i].dump(depth+1, f'{i} = ', test)
        for j, k in enumerate(self.nest):
            ret += k.dump(depth+1, f'{j}:', test)
        return ret

    def head(self, prefix='', test=False):
        xid = '' if test else f' @{id(self):x}'
        return f'{prefix}<{self.type}:{self.value}>{xid}'

    def pad(self, depth, tab):
        return f'\n{tab*depth}'

    def synq(self):
        def s(): synqueue.put(self, block=False)
        try:
            s()
        except queue.Full:
            sync()
            s()
        return self

    def sync(self):
        ret = self.synced
        if not self.synced:
            self.synced = True
            print(self.head(prefix='sync: '))
        return self.synced

    def __floordiv__(self, that):
        if isinstance(that, str):
            that = S(that)
        assert isinstance(that, Object)
        self.nest.append(that)
        return self.synq()

    def file(self, to):
        return self.dump(tab=to.tab)


class Primitive(Object):
    pass


class S(Primitive):

    def __init__(self, begin=None, end='', pfx=None, inline=False):
        V = f'{begin}' if begin != None else ''
        super().__init__(V)
        self.begin = begin
        self.end = end
        self.pfx = pfx
        self.inline = inline

    def file(self, to, depth=0):
        ret = ''
        #
        if self.pfx != None:
            ret += f'{to.tab*depth}{self.pfx}\n'
        #
        if self.begin != None:
            ret += f'{to.tab*depth}{self.value}'
        #
        if self.inline:
            for j in self.nest:
                ret += f'{j.value}'
        else:
            ret += '\n'
            for j in self.nest:
                ret += j.file(to, depth+1)
        #
        if self.end:
            if self.inline:
                ret += f'{self.end}'
            else:
                ret += f'{to.tab*depth}{self.end}\n'
        return ret


class Section(S):
    def file(self, to, depth=0):
        def s(c):
            return f'{to.tab*depth}{to.comment} {c} {self.head(test=True)}{to.commend}\n'
        ret = ''
        if self.nest:
            ret += s('\\')
            for j in self.nest:
                ret += j.file(to, depth+0)
            ret += s('/')
        return ret


class IO(Object):
    pass


class Dir(IO):

    def __init__(self, V):
        assert re.match(r'\.?[a-z]+', V)
        super().__init__(V)
        self.path = V

    def sync(self):
        if super().sync():
            try:
                os.mkdir(self.path)
            except FileExistsError:
                pass

    def __floordiv__(self, that):
        if isinstance(that, File):
            that.path = f'{self.path}/{that.value}'
            return super().__floordiv__(that)
        if isinstance(that, Dir):
            that.path = f'{self.path}/{that.value}'
            return super().__floordiv__(that)
        raise TypeError(that)


class File(IO):

    def __init__(self, V, ext='', tab=' '*4, comment='#'):
        super().__init__(f'{V}{ext}')
        self.ext = ext
        self.tab = tab
        self.comment = comment
        self.commend = ''
        if self.comment == '/*':
            self.commend = ' */'

    def sync(self):
        if super().sync():
            with open(self.path, 'w') as W:
                for j in self.nest:
                    W.write(j.file(self))


class mkFile(File):
    def __init__(self, V='Makefile', ext='', tab='\t', comment='#'):
        super().__init__(V, ext, tab, comment)


class jsonFile(File):
    def __init__(self, V, ext='.json', comment='/*'):
        super().__init__(V, ext, comment=comment)


class Module(Object):
    pass


class dirModule(Module):
    def __init__(self, V=None):
        if not V:
            V = __import__('sys').argv[0]
            V = V.split('/')[-1]
            V = V.split('.')[0]
        super().__init__(V)
        self.d = Dir(f'{self}')
        self.init_mk()
        self.init_apt()
        self.init_giti()
        self.init_meta()
        self.init_readme()
        self.init_vscode()

    def init_vscode(self):
        self.d.vscode = Dir('.vscode')
        self.d // self.d.vscode
        self.init_vscode_settings()
        self.init_vscode_extensions()

    def init_vscode_settings(self):
        self.d.vscode.settings = Section('settings')
        self.d.vscode.settings.multi = Section('multi')
        self.d.vscode.settings // self.d.vscode.settings.multi
        #

        def multi(key, cmd):
            return (S('{', '},') //
                    S(f'"command": "multiCommand.{key}",') //
                    (S('"sequence": [') //
                     '"workbench.action.files.saveAll",' //
                     (S('{"command": "workbench.action.terminal.sendSequence","args": {"text":', '}}]') //
                        (S(f'"\\u000D', '\\u000D"\n', inline=True) //
                         self.d.vscode.settings.f12))))
        self.d.vscode.settings.f12 = S('clear;make')
        self.d.vscode.settings.multi //\
            (S('"multiCommand.commands": [', '],') //
             multi('f12', self.d.vscode.settings.f12))
        #
        self.d.vscode.settings.watcher = Section('watcher')
        self.d.vscode.settings // self.d.vscode.settings.watcher

        #
        self.d.vscode.settings.exclude = Section('exclude')
        self.d.vscode.settings // self.d.vscode.settings.exclude
        #
        self.d.vscode.settings.assoc = Section('assoc')
        self.d.vscode.settings // self.d.vscode.settings.assoc
        #
        self.d.vscode //\
            (jsonFile('settings') //
             (S('{', '}') //
              self.d.vscode.settings.multi //
              (S('"files.watcherExclude": {', '},') //
               self.d.vscode.settings.watcher) //
                (S('"files.exclude": {', '},') //
                 self.d.vscode.settings.exclude) //
                (S('"files.associations": {', '},') //
                 self.d.vscode.settings.assoc) //
                '"editor.tabSize": 4'))

    def init_vscode_extensions(self):
        self.d.vscode.extensions = Section('extensions')
        self.d.vscode //\
            (jsonFile('extensions') //
             (S('{', '}') //
                (S('"recommendations": [', ']') //
                 '"stkb.rewrap",' //
                 self.d.vscode.extensions)))

    def init_mk(self):
        self.d.mk = mkFile()
        self.d // self.d.mk
        #
        self.d.mk.var = Section('var')
        self.d.mk //\
            (self.d.mk.var //
             f'{"MODULE":<9} = $(notdir $(CURDIR))' //
             f'{"OS":<9} = $(shell uname -s)' //
             f'{"MACHINE":<9} = $(shell uname -m)')
        #
        self.d.mk.dir = Section('dir')
        self.d.mk //\
            (self.d.mk.dir //
             f'{"CWD":<9} = $(CURDIR)' //
             f'{"DOC":<9} = $(CWD)/doc' //
             f'{"BIN":<9} = $(CWD)/bin' //
             f'{"SRC":<9} = $(CWD)/src' //
             f'{"TMP":<9} = $(CWD)/tmp'
             )
        #
        self.d.doc = Dir('doc')
        self.d // (self.d.doc // File('.gitignore'))
        self.d.bin = Dir('bin')
        self.d // (self.d.bin // File('.gitignore'))
        self.d.src = Dir('src')
        self.d // (self.d.src // File('.gitignore'))
        self.d.tmp = Dir('tmp')
        self.d // (self.d.tmp // File('.gitignore'))
        #
        self.d.mk.tool = Section('tool')
        self.d.mk //\
            (self.d.mk.tool //
             f'{"WGET":<9} = wget -c')
        #
        self.d.mk.obj = Section('obj')
        self.d.mk // self.d.mk.obj
        #
        self.d.mk.all = Section('all')
        self.d.mk.all.target = S()
        self.d.mk.all.body = S()
        self.d.mk //\
            (self.d.mk.all //
             (S('all:', pfx='.PHONY: all', inline=True) //
              self.d.mk.all.target) //
             (self.d.mk.all.body)
             )
        #
        self.d.mk.inst = Section('inst')
        self.d.mk.install = Section('install')
        self.d.mk.update = Section('update')
        self.d.mk //\
            (self.d.mk.inst //
             (S('install: $(OS)_install', pfx='.PHONY: install') //
              self.d.mk.install) //
             (S('update: $(OS)_update', pfx='.PHONY: update') //
              self.d.mk.update) //
             (S('$(OS)_install $(OS)_update:', pfx='.PHONY: $(OS)_install $(OS)_update') //
              'sudo apt update'//'sudo apt install -u `cat apt.txt`')
             )

    def init_apt(self):
        self.d.apt = File('apt.txt')
        self.d // self.d.apt
        self.d.apt // 'git make wget'

    def init_giti(self):
        self.d.giti = File('.gitignore')
        self.d // self.d.giti
        self.d.giti // '*~' // '*.swp' // '*.log'

    def init_meta(self):
        self.MODULE = self.TITLE = self
        self.AUTHOR = 'Dmitry Ponyatov'
        self.EMAIL = 'dponyatov@gmail.com'
        self.YEAR = '2020'
        self.LICENSE = 'MIT'
        self.GITHUB = 'https://github.com/ponyatov'
        self.ABOUT = """
"""

    def __setattr__(self, key, that):
        super().__setattr__(key, that)
        if key in ['TITLE', 'ABOUT']:
            try:
                self.init_readme()
            except AttributeError:
                pass
        return self

    def init_readme(self):
        self.d.readme = File('README.md')
        self.d // self.d.readme
        self.d.readme //\
            f'#  {self.MODULE}' //\
            f'## {self.TITLE}' //\
            '' //\
            f'(c) {self.AUTHOR} <<{self.EMAIL}>> {self.YEAR} {self.LICENSE}' //\
            f'{self.ABOUT}' //\
            f'github: {self.GITHUB}/{self.MODULE}'


class pyModule(dirModule):
    def __init__(self, V=None):
        super().__init__(V)


class rsFile(File):
    def __init__(self, V, ext='.rs', comment='//'):
        super().__init__(V, ext)


class Meta(Object):
    pass


class Fn(Meta):
    pass


class rsFn(Fn):
    def file(self, to):
        ret = S(f'fn {self.value}() {{', '}')
        for j in self.nest:
            ret // j
        return ret.file(to)


class rsModule(dirModule):
    def __init__(self, V=None):
        super().__init__(V)
        self.init_rust()

    def init_rust(self):
        self.init_cargo()
        self.d.src.main = rsFile('main')
        self.d.src // self.d.src.main
        self.d.src.main //\
            'mod hello;' //\
            (rsFn('main') // 'hello::hello();')

    def init_giti(self):
        super().init_giti()
        self.d.giti // '' // '/target/' // '/Cargo.lock'

    def init_apt(self):
        super().init_apt()
        self.d.apt // 'curl'

    def init_readme(self):
        super().init_readme()
        self.d.readme.rust = S('### Rust', pfx='')
        self.d.readme // self.d.readme.rust

    def init_mk(self):
        super().init_mk()
        self.d.mk.dir //\
            f'{"CARGOBIN":<9} = $(HOME)/.cargo/bin'
        self.d.mk.tool //\
            f'{"RUSTUP":<9} = $(CARGOBIN)/rustup' //\
            f'{"CARGO":<9} = $(CARGOBIN)/cargo' //\
            f'{"RUSTC":<9} = $(CARGOBIN)/rustc'
        self.d.mk.all.body //\
            '$(CARGO) run'
        self.d.mk.install //\
            '$(MAKE)   $(RUSTUP)' //\
            '$(RUSTUP) update' //\
            '$(RUSTUP) component add rustfmt' //\
            '$(CARGO)  build'
        self.d.mk.update //\
            '$(RUSTUP) update'
        self.d.mk.inst //\
            (S('$(RUSTUP) $(CARGO) $(RUSTC):') //
             "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")

    def init_vscode_settings(self):
        super().init_vscode_settings()
        self.d.vscode.settings.watcher //\
            '"**/target/**":true,'
        self.d.vscode.settings.exclude //\
            '"**/target/**":true,'

    def init_vscode_extensions(self):
        super().init_vscode_extensions()
        self.d.vscode.extensions //\
            '"bungcip.better-toml",' //\
            '"rust-lang.rust",'

    def init_cargo(self):
        self.d.cargo = File('Cargo', ext='.toml')
        self.d // self.d.cargo
        #
        self.d.cargo.package = Section('package')
        self.d.cargo //\
            (self.d.cargo.package //
             '[package]' //
             f'{"name":<9} = "{self:l}"' //
             f'{"version":<9} = "0.0.1"' //
             f'{"authors":<9} = ["{self.AUTHOR} <{self.EMAIL}>"]' //
             f'{"edition":<9} = "2018"')
        #
        self.d.cargo.dependencies = Section('dependencies')
        self.d.cargo //\
            (self.d.cargo.dependencies//'[dependencies]')
