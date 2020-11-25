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
        assert not spec
        return f'{self.value}'

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

    def __init__(self, V, pfx=None):
        super().__init__(V)
        self.pfx = pfx

    def file(self, to, depth=0):
        ret = ''
        if self.pfx != None:
            ret += f'{to.tab*depth}{self.pfx}\n'
        ret += f'{to.tab*depth}{self.value}\n'
        for j in self.nest:
            ret += j.file(to, depth+1)
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
        assert re.match(r'[a-z]+', V)
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

    def sync(self):
        if super().sync():
            with open(self.path, 'w') as W:
                for j in self.nest:
                    W.write(j.file(self))


class mkFile(File):
    def __init__(self, V='Makefile', ext='', tab='\t', comment='#'):
        super().__init__(V, ext, tab, comment)


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

    def init_mk(self):
        self.d.mk = mkFile()
        self.d // self.d.mk
        #
        self.d.mk.var = Section('var')
        self.d.mk //\
            (self.d.mk.var //
             f'{"MODULE":<11} = $(notdir $(CURDIR))' //
             f'{"OS":<11} = $(shell uname -s)' //
             f'{"MACHINE":<11} = $(shell uname -m)')
        #
        self.d.mk.dir = Section('dir')
        self.d.mk //\
            (self.d.mk.dir //
             f'{"CWD":<11} = $(CURDIR)' //
             f'{"DOC":<11} = $(CWD)/doc' //
             f'{"BIN":<11} = $(CWD)/bin' //
             f'{"SRC":<11} = $(CWD)/src' //
             f'{"TMP":<11} = $(CWD)/tmp'
             )
        for i in ['doc', 'bin', 'src', 'tmp']:
            ii = Dir(i)
            self.d // ii
            ii.giti = File('.gitignore')
            ii // ii.giti

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


class rsModule(dirModule):
    def __init__(self, V=None):
        super().__init__(V)

    def init_apt(self):
        super().init_apt()
        self.d.apt // 'cargo rustc'

    def init_readme(self):
        super().init_readme()
        self.d.readme.rust = S('### Rust', pfx='')
        self.d.readme // self.d.readme.rust
