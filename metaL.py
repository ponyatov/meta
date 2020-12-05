# generative metaprogramming

import os
import sys
import re

import xxhash

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

    ######################################################################

    def __format__(self, spec):
        if spec == '':
            return f'{self.value}'
        if spec == 'l':
            return f'{self.value.lower()}'
        if spec == 'u':
            return f'{self.value.upper()}'
        if spec == 'm':
            return f'{self.value.capitalize()}'
        raise TypeError(spec)

    ######################################################################

    def test(self): return self.dump(test=True)

    def dump(self, depth=0, prefix='', tab='\t', test=False):
        ret = self.pad(depth, tab)
        ret += self.head(prefix, test)
        for i in self.keys():
            ret += self[i].dump(depth+1, f'{i} = ', test=test)
        for j, k in enumerate(self.nest):
            ret += k.dump(depth+1, f'{j}: ', test=test)
        return ret

    def head(self, prefix='', test=False):
        xid = '' if test else f' @{id(self):x}'
        return f'{prefix}<{self.type}:{self.value}>{xid}'

    def pad(self, depth, tab):
        return f'\n{tab*depth}'

    ######################################################################

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
            # print(self.head(prefix='sync: '))
        return self.synced

    def file(self, to, depth=0):
        return self.dump(depth, tab=to.tab)

    ######################################################################

    def keys(self):
        return sorted(self.slot.keys())

    def __getitem__(self, key):
        assert isinstance(key, str)
        return self.slot[key]

    def __setitem__(self, key, that):
        assert isinstance(key, str)
        if isinstance(that, str):
            that = S(that)
        assert isinstance(that, Object)
        self.slot[key] = that
        return self

    def __floordiv__(self, that):
        if isinstance(that, str):
            that = S(that)
        assert isinstance(that, Object)
        self.nest.append(that)
        return self.synq()

    ######################################################################

    def drop(self): self.nest.pop(); return self

#######################################################################################


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
            ret += ' '.join(map(lambda j:
                                re.sub(r'[\r\n\t]+', '', j.file(to)),
                                self.nest))
        else:
            ret += '\n' if self.begin != None else ''
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

#######################################################################################


class IO(Object):
    pass


class Dir(IO):

    def __init__(self, V):
        assert re.match(r'\.?[a-zA-Z]+', V)
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

    def __init__(self, V, ext='', comment='#', tab=' '*4):
        super().__init__(f'{V}{ext}')
        #
        self.ext = ext
        self.tab = tab
        self.comment = comment
        self.commend = ''
        if self.comment == '/*':
            self.commend = ' */'
        if self.comment == '<!--':
            self.commend = ' -->'
        #
        self.top = Section('top')
        self.mid = Section('mid')
        self.bot = Section('bot')
        self // self.top // self.mid // self.bot

    def sync(self):
        if super().sync():
            if hasattr(self, 'path'):
                with open(self.path, 'w') as W:
                    for j in self.nest:
                        W.write(j.file(self))

#######################################################################################


class Module(Object):
    pass


class mkFile(File):
    def __init__(self, V='Makefile', ext='.mk', comment='#',  tab='\t'):
        super().__init__(V, ext, comment, tab)


class jsonFile(File):
    def __init__(self, V, ext='.json', comment='/*'):
        super().__init__(V, ext, comment)

#######################################################################################


class iniFile(File):
    def __init__(self, V, ext='.ini', comment='#'):
        super().__init__(V, ext, comment)


class gitiFile(File):
    def __init__(self, V='', ext='.gitignore', comment='#'):
        super().__init__(V, ext, comment)
        self.bot // '!.gitignore'


class dirModule(Module):
    def __init__(self, V=None):
        if not V:
            V = __import__('sys').argv[0]
            V = V.split('/')[-1]
            V = V.split('.')[0]
        super().__init__(V)
        self.d = Dir(f'{self}')
        self.init_config()
        self.init_mk()
        self.init_apt()
        self.init_giti()
        self.init_meta()
        self.init_readme()
        self.init_vscode()

    def init_config(self):
        self.config = Section('config')
        self.config.SECRET_KEY = \
            xxhash.xxh128(self.head(test=True)).hexdigest()
        self.config.HOST = '127.0.0.1'
        self.config.HOST_tuple = '{%s}' % re.sub(r'\.', r',', self.config.HOST)

        def scale(hash32):
            A = float(1024)
            B = float(0xBFFF)
            # 0          -> A
            # 0xFFFFFFFF -> B
            port = int(A + ((B - A) / 0xFFFFFFFF) * hash32)
            assert A <= port and port <= B
            return port
        self.config.PORT = scale(xxhash.xxh32(
            self.head(test=True)).intdigest())
        assert self.config.PORT in range(1024, 0xBFFF)

    def init_vscode(self):
        self.d.vscode = Dir('.vscode')
        self.d // self.d.vscode
        self.init_vscode_tasks()
        self.init_vscode_settings()
        self.init_vscode_extensions()

    def vscode_task(self, it):
        return (S('{', '},') //
                f'"label":          "make: {it}",' //
                f'"type":           "shell",' //
                f'"command":        "make {it}",' //
                f'"problemMatcher": []')

    def init_vscode_tasks(self):
        self.d.vscode.tasks = jsonFile('tasks')
        self.d.vscode // self.d.vscode.tasks
        self.d.vscode.tasks.tasks = Section('tasks')
        self.d.vscode.tasks.tasks //\
            self.vscode_task('install') //\
            self.vscode_task('update')
        self.d.vscode.tasks //\
            (S("{", "}") //
             '"version": "2.0.0",' //
             (S('"tasks": [', ']') //
              self.d.vscode.tasks.tasks))

    def init_vscode_settings(self):
        self.d.vscode.settings = jsonFile('settings')
        self.d.vscode // self.d.vscode.settings
        self.d.vscode.settings.top // '{'
        self.d.vscode.settings.bot // '}'

        #
        self.d.vscode.settings.multi = Section('multi')
        self.d.vscode.settings.mid // self.d.vscode.settings.multi

        def multi(key, cmd):
            return (S('{', '},') //
                    S(f'"command": "multiCommand.{key}",') //
                    (S('"sequence": [') //
                     '"workbench.action.files.saveAll",' //
                     (S('{"command": "workbench.action.terminal.sendSequence","args": {"text":', '}}]') //
                        (S(f'"\\u000D', '\\u000D"\n', inline=True) // cmd))))
        self.d.vscode.settings.f11 = S('clear;make')
        self.d.vscode.settings.f12 = S('clear;make')
        self.d.vscode.settings.multi //\
            (S('"multiCommand.commands": [', '],') //
             multi('f11', self.d.vscode.settings.f11) //
             multi('f12', self.d.vscode.settings.f12))
        #
        self.d.vscode.settings.watcher = Section('watcher')
        self.d.vscode.settings.mid //\
            (S('"files.watcherExclude": {', '},') //
             self.d.vscode.settings.watcher)
        #
        self.d.vscode.settings.exclude = Section('exclude')
        self.d.vscode.settings.mid //\
            (S('"files.exclude": {', '},') //
             self.d.vscode.settings.exclude)
        #
        self.d.vscode.settings.assoc = Section('assoc')
        self.d.vscode.settings.mid //\
            (S('"files.associations": {', '},') //
             self.d.vscode.settings.assoc)
        #
        self.d.vscode.settings.mid //\
            '"editor.tabSize": 4,' //\
            '"workbench.tree.indent": "32",'

    def init_vscode_extensions(self):
        self.d.vscode.extensions = Section('extensions')
        self.d.vscode //\
            (jsonFile('extensions') //
             (S('{', '}') //
                (S('"recommendations": [', ']') //
                 '"stkb.rewrap",' //
                 '"tabnine.tabnine-vscode",' //
                 self.d.vscode.extensions)))

    def init_giti(self):
        super().init_giti()
        self.d.giti // f'/{self}_??????.pdf'

    def init_mk(self):
        self.d.mk = mkFile(ext='')
        self.d // self.d.mk
        #
        self.d.mk.var = Section('var')
        self.d.mk //\
            (self.d.mk.var //
             f'{"MODULE":<9}  = $(notdir $(CURDIR))' //
             f'{"OS":<9}  = $(shell uname -s)' //
             f'{"MACHINE":<9}  = $(shell uname -m)' //
             f'{"NOW":<9}  = $(shell date +%d%m%y)' //
             f'{"REL":<9}  = $(shell git rev-parse --short=4 HEAD)'
             )
        #
        self.d.mk.dir = Section('dir')
        self.d.mk //\
            (self.d.mk.dir //
             f'{"CWD":<9}  = $(CURDIR)' //
             f'{"DOC":<9}  = $(CWD)/doc' //
             f'{"BIN":<9}  = $(CWD)/bin' //
             f'{"SRC":<9}  = $(CWD)/src' //
             f'{"TMP":<9}  = $(CWD)/tmp'
             )
        #
        self.d.doc = Dir('doc')
        self.d // self.d.doc
        self.d.doc.giti = gitiFile()
        self.d.doc // self.d.doc.giti
        self.d.doc.giti.top // '*.pdf'
        #
        self.d.bin = Dir('bin')
        self.d // self.d.bin
        self.d.bin.giti = gitiFile()
        self.d.bin // self.d.bin.giti
        self.d.bin.giti.top // '*'
        #
        self.d.src = Dir('src')
        self.d // (self.d.src // gitiFile())
        #
        self.d.tmp = Dir('tmp')
        self.d // self.d.tmp
        self.d.tmp.giti = gitiFile()
        self.d.tmp // self.d.tmp.giti
        self.d.tmp.giti.top // '*'
        #
        self.d.mk.tool = Section('tool')
        self.d.mk //\
            (self.d.mk.tool //
             f'{"WGET":<9}  = wget -c')
        #
        self.d.mk.obj = Section('obj')
        self.d.mk // self.d.mk.obj
        self.d.mk.obj.c = Section('c')
        self.d.mk.obj // self.d.mk.obj.c
        self.d.mk.obj.h = Section('h')
        self.d.mk.obj // self.d.mk.obj.h
        self.d.mk.obj.s = Section('s')
        self.d.mk.obj // self.d.mk.obj.s
        #
        self.d.mk.cfg = Section('cfg')
        self.d.mk // self.d.mk.cfg
        #
        self.d.mk.all = Section('all')
        self.d.mk // self.d.mk.all
        self.d.mk.all.target = S(' ', inline=True)
        self.d.mk.all.body = Section('body')
        self.d.mk.all //\
            (S('all:', pfx='.PHONY: all', inline=True) //
             self.d.mk.all.target) //\
            (S() // '' //
             self.d.mk.all.body)
        #
        self.d.mk.rule = Section('rules')
        self.d.mk // self.d.mk.rule
        #
        self.d.mk.install = Section('install')
        self.d.mk.install.body = Section('body')
        self.d.mk.install.post = Section('post')
        self.d.mk.update = Section('update')
        self.d.mk //\
            (self.d.mk.install //
             (S('install: $(OS)_install', pfx='.PHONY: install') //
              self.d.mk.install.body //
              self.d.mk.install.post) //
             (S('update: $(OS)_update', pfx='.PHONY: update') //
              self.d.mk.update) //
             (S('$(OS)_install $(OS)_update:', pfx='.PHONY: $(OS)_install $(OS)_update') //
              'sudo apt update'//'sudo apt install -u `cat apt.txt`')
             )
        #
        self.d.mk.merge = Section('merge')
        self.d.mk // self.d.mk.merge
        self.d.mk.merge //\
            'MERGE  = Makefile README.md apt.txt .gitignore .vscode $(S)'
        self.d.mk.merge //\
            (S('main:', pfx='.PHONY: main') //
             'git push -v' //
             'git checkout $@' //
             'git pull -v' //
             'git checkout shadow -- $(MERGE)')
        self.d.mk.merge //\
            (S('shadow:', pfx='.PHONY: shadow') //
             'git pull -v' //
             'git checkout $@' //
             'git pull -v')
        self.d.mk.merge //\
            (S('release:', pfx='.PHONY: release') //
             'git tag $(NOW)-$(REL)' //
             'git push -v && git push -v --tags' //
             '$(MAKE) shadow')

    def init_apt(self):
        self.d.apt = File('apt.txt')
        self.d // self.d.apt
        self.d.apt // 'git make wget'

    def init_giti(self):
        self.d.giti = gitiFile()
        self.d // self.d.giti
        self.d.giti.top // '*~' // '*.swp' // '*.log'

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
        if key in ['TITLE', 'ABOUT', 'GITHUB']:
            try:
                self.init_readme()
            except AttributeError:
                pass
        return self

    def init_readme(self):
        self.d.readme = File('README.md')
        self.d // self.d.readme
        self.d.readme //\
            f'#  `{self}`' //\
            f'## {self.TITLE}' //\
            '' //\
            f'(c) {self.AUTHOR} <<{self.EMAIL}>> {self.YEAR} {self.LICENSE}' //\
            f'{self.ABOUT}' //\
            f'github: {self.GITHUB}/{self.MODULE}'

#######################################################################################


class pyFile(File):
    def __init__(self, V, ext='.py', comment='#'):
        super().__init__(V, ext, comment)


class pyModule(dirModule):
    def __init__(self, V=None):
        super().__init__(V)
        self.init_py()

    def init_py(self):
        self.init_reqs()
        self.d.py = pyFile(self)
        self.d // self.d.py

    def init_config(self):
        super().init_config()
        self.d.config = pyFile('config')
        self.d // self.d.config
        self.d.config //\
            f'{"SECRET_KEY":<11} = "{self.config.SECRET_KEY}"' //\
            f'{"HOST":<11} = "{self.config.HOST}"' //\
            f'{"PORT":<11} = {self.config.PORT}'

    def init_mk(self):
        super().init_mk()
        self.d.mk.tool //\
            f'{"PY":<9}  = $(BIN)/python3' //\
            f'{"PIP":<9}  = $(BIN)/pip3' //\
            f'{"PEP":<9}  = $(BIN)/autopep8' //\
            f'{"PYT":<9}  = $(BIN)/pytest'
        #
        self.d.mk.obj // f'{"S":<3} += $(MODULE).py'
        #
        self.d.mk.all.target // '$(PY) $(MODULE).py'
        self.d.mk.all.body // '$^'
        #
        self.d.mk.alls //\
            (S('pep: $(PEP) $(S)', pfx='.PHONY: pep') //
                '$(PEP) --in-place $(S)')
        #
        self.d.mk.pyinst = Section('pyinst')
        self.d.mk.install // self.d.mk.pyinst
        self.d.mk.install.body //\
            '$(MAKE) $(PIP)' //\
            '$(MAKE) update'
        self.d.mk.update //\
            '$(PIP) install -U pip autopep8' //\
            '$(PIP) install -U -r requirements.pip'
        self.d.mk.pyinst //\
            (S('$(PY) $(PIP):')//'python3 -m venv .' // '$(MAKE) update')

    def init_reqs(self):
        self.d.reqs = File('requirements.pip')
        self.d // self.d.reqs

    def init_giti(self):
        super().init_giti()
        self.d.giti.mid //\
            '*.pyc' //\
            '/bin' //\
            '/lib' //\
            '/lib64' //\
            '/share' //\
            '/__pycache__' //\
            '/pyvenv.cfg'

    def init_vscode_settings(self):
        super().init_vscode_settings()
        self.d.vscode.settings.top //\
            '"python.pythonPath"              : "./bin/python3",' //\
            '"python.formatting.provider"     : "autopep8",' //\
            '"python.formatting.autopep8Path" : "./bin/autopep8",' //\
            '"python.formatting.autopep8Args" : ["--ignore=E26,E302,E401,E402"],'

        pyfiles = (S() //
                   '"**/__pycache__/**": true,' //
                   '"**/bin/**": true, "**/include/**": true, "**/lib*/**": true,' //
                   '"**/share/**": true, "**/*.pyc": true, "**/pyvenv.cfg": true,')
        self.d.vscode.settings.watcher // pyfiles
        self.d.vscode.settings.exclude // pyfiles
        self.d.vscode.settings.assoc //\
            '"**/*.py": "python",' // '"requirements.*": "config",'

#######################################################################################


class cssFile(File):
    def __init__(self, V, ext='.css', comment='/*'):
        super().__init__(V, ext, comment)


class htmlFile(File):
    def __init__(self, V, ext='.html', comment='<!--'):
        super().__init__(V, ext, comment)


class HTML(S):
    def __init__(self, V=None, inline=False, **kwargs):
        super().__init__(V, inline=inline)
        for i in kwargs:
            self[i] = kwargs[i]

    def file(self, to, depth=0):
        # <CLASS
        ret = ''
        ret += f'{to.tab*depth}<{self.type.upper()}'
        #
        for i in self.keys():
            ret += f' {i}="{self[i]}"'
        ret += '>'
        if not self.inline:
            ret += '\n'
        for j in self.nest:
            if not self.inline:
                ret += j.file(to, depth+1)
            else:
                ret += j.file(to, 0)[:-1]
        if not self.inline:
            ret += f'{to.tab*depth}'
        ret += f'</{self.type.upper()}>\n'
        # if not self.inline:
        #     ret += '\n'
        return ret


class TABLE(HTML):
    pass


class TR(HTML):
    pass


class TD(HTML):
    pass


class A(HTML):
    pass


class IMG(HTML):
    pass


class P(HTML):
    def __init__(self, V):
        super().__init__(inline=True)
        self // V


class webModule(pyModule):

    def __init__(self, V=None):
        super().__init__(V)
        webModule.mixin(self)

    def mixin(self):
        webModule.mixin_static(self)
        webModule.mixin_templates(self)
        webModule.mixin_mk(self)

    def mixin_mk(self):
        self.d.mk.js = Section('js')
        self.d.mk.install // self.d.mk.js
        self.d.mk.install.body //\
            '$(MAKE) js'
        self.d.mk.js //\
            (S('js: \\', pfx='.PHONY: js') //
                "static/jquery.js \\" //
                "static/bootstrap.css static/bootstrap.js \\" //
                "static/leaflet.css static/leaflet.js")
        self.d.mk.js // '' //\
            'JQUERY_VER = 3.5.1' //\
            'JQUERY_JS  = https://code.jquery.com/jquery-$(JQUERY_VER).min.js' //\
            (S("static/jquery.js:") //
                "$(WGET) -O $@ $(JQUERY_JS)")
        self.d.mk.js // '' //\
            'BOOTSTRAP_VER = 3.4.1' //\
            (S("static/bootstrap.css:") //
                "$(WGET) -O $@ https://bootswatch.com/3/darkly/bootstrap.min.css") //\
            (S("static/bootstrap.js:") //
                "$(WGET) -O $@ https://maxcdn.bootstrapcdn.com/bootstrap/$(BOOTSTRAP_VER)/js/bootstrap.min.js")
        self.d.mk.js // '' //\
            'LEAFLET_VER = 1.7.1' //\
            'LEAFLET_ZIP = http://cdn.leafletjs.com/leaflet/v$(LEAFLET_VER)/leaflet.zip' //\
            (S('$(TMP)/leaflet.zip:') //
                '$(WGET) -O $@ $(LEAFLET_ZIP)') //\
            'static/leaflet.css: static/leaflet.js' //\
            (S('static/leaflet.js: $(TMP)/leaflet.zip') //
             'unzip -d static $< leaflet.css leaflet.js* images/* && touch $@')

        #
        self.d.mk.merge // 'MERGE += static templates'

    def init_static(self):
        webModule.mixin_static(self)

    def mixin_static(self):
        self.d.static = Dir('static')
        self.d // self.d.static
        self.d.static.giti = gitiFile()
        self.d.static // self.d.static.giti
        self.d.static.giti //\
            'jquery.js' // 'bootstrap.*' //\
            'leaflet.*' // 'images/layers*.png' // 'images/marker-*.png'
        #
        self.d.static.css = cssFile('css')
        self.d.static // self.d.static.css

    def init_templates(self):
        webModule.mixin_templates(self)

    def mixin_templates(self):
        self.d.templates = Dir('templates')
        self.d // self.d.templates
        self.d.templates // gitiFile()
        #
        self.d.templates.all = htmlFile('all')
        self.d.templates // self.d.templates.all
        self.d.templates.all //\
            '<!doctype html>' //\
            (S('<html lang="ru">', '</html>') //
             (S('<head>', '</head>') //
                '<meta charset="utf-8">' //
                '<meta http-equiv="X-UA-Compatible" content="IE=edge">' //
                '<meta name="viewport" content="width=device-width, initial-scale=1">' //
                '<link href="/static/bootstrap.css" rel="stylesheet">' //
                '<link rel="shortcut icon" href="/static/logo.png" type="image/png">' //
                '<link href="/static/css.css" rel="stylesheet">' //
                '{% block head %}{% endblock %}'
              ) //
             (S('<style>', '</style>') // '{% block style %}{% endblock %}') //
                (S('<body>', '</body>') // '{% block body %}{% endblock %}') //
                '<script src="/static/jquery.js"></script>' //
                '<script src="/static/bootstrap.js"></script>' //
                '{% block script %}{% endblock %}'
             )
        #
        self.d.templates.index = htmlFile('index')
        self.d.templates // self.d.templates.index
        self.d.templates.index.top //\
            "{% extends 'all.html' %}" // "{% block body %}"
        self.d.templates.index.bot //\
            "{% endblock %}"


class djModule(webModule):
    def __init__(self, V=None):
        super().__init__(V)
        self.init_dj()

    def init_vscode_tasks(self):
        super().init_vscode_tasks()
        self.d.vscode.tasks.tasks //\
            self.vscode_task('migrate') //\
            self.vscode_task('makemigrations') //\
            self.vscode_task('createsuperuser')

    def init_dj(self):
        self.d.dj = Dir('dj')
        self.d // self.d.dj
        self.init_dj_settings()
        self.init_dj_urls()
        self.init_dj_views()

    def init_dj_urls(self):
        self.d.dj.urls = pyFile('urls')
        self.d.dj // self.d.dj.urls
        self.d.dj.urls.top //\
            'from django.contrib import admin' //\
            'from django.urls import path' //\
            'from dj import views'
        self.d.dj.urls.mid //\
            (S('urlpatterns = [', ']') //
             "path('', views.index, name='index')," //
             "path('admin/', admin.site.urls, name='admin'),")

    def init_dj_views(self):
        self.d.dj.views = pyFile('views')
        self.d.dj // self.d.dj.views
        self.d.dj.views.top //\
            'from django.http import HttpResponse, HttpResponseRedirect' //\
            'from django.template import loader'
        self.d.dj.views.mid //\
            (S('def index(request):') //
             (S('if not request.user.is_authenticated:') //
              "return HttpResponseRedirect(f'/admin/login/?next={request.path}')") //
             "template = loader.get_template('index.html')" //
             (S('context = {', '}')//'') //
             "return HttpResponse(template.render(context, request))")

    def init_dj_settings(self):
        self.d.dj.settings = pyFile('settings')
        self.d.dj // self.d.dj.settings
        self.d.dj.settings //\
            'import config' //\
            '' //\
            f'{"SECRET_KEY":<12} = config.SECRET_KEY' //\
            f'{"DEBUG":<12} = True' //\
            f'{"ROOT_URLCONF":<12} = "dj.urls"'
        #
        self.d.dj.settings // '' //\
            "from pathlib import Path" //\
            "BASE_DIR = Path(__file__).resolve(strict=True).parent.parent"
        #
        apps = S('INSTALLED_APPS = [', ']')
        self.d.dj.settings // '' // apps
        for i in ['admin', 'auth', 'contenttypes', 'sessions', 'messages', 'staticfiles']:
            apps // f"'django.contrib.{i}',"
        self.d.dj.settings // '' //\
            f"{'STATIC_URL':<17} = '/static/'" //\
            f"{'STATICFILES_DIRS':<17} = [BASE_DIR/'static']"
        #
        self.d.dj.settings // '' //\
            (S('TEMPLATES = [', ']') //
             (S('{', '}') //
              "'BACKEND'  : 'django.template.backends.django.DjangoTemplates'," //
              "'DIRS'     : [BASE_DIR/'templates'], # req for /template resolve" //
              "'APP_DIRS' : True, # req for admin/login.html template" //
              (S("'OPTIONS'  : {", "}") //
               (S("'context_processors': [", "]") //
                "'django.template.context_processors.request'," //
                "'django.contrib.auth.context_processors.auth'," //
                "'django.contrib.messages.context_processors.messages',"
                ))))
        #
        self.d.dj.settings // '' //\
            (S("MIDDLEWARE = [", "]") //
             "'django.contrib.sessions.middleware.SessionMiddleware'," //
             "'django.contrib.auth.middleware.AuthenticationMiddleware'," //
             "'django.contrib.messages.middleware.MessageMiddleware',")
        #
        self.d.dj.settings // '' //\
            (S("DATABASES = {", "}") //
             (S("'default': {", "}") //
              "'ENGINE': 'django.contrib.gis.db.backends.spatialite'," //
              f"'NAME': BASE_DIR/'{self}.sqlite3',"))
        #
        self.d.dj.settings // '' //\
            "LANGUAGE_CODE = 'ru-ru'" //\
            "DATE_FORMAT = '%d/%m/%Y'" //\
            "DATETIME_FORMAT = '%m/%d/%Y %H:%M:%S'"

    def init_apt(self):
        super().init_apt()
        self.d.apt //\
            'sqlite3 sqlitebrowser' //\
            'libsqlite3-mod-spatialite libspatialite7 gdal-bin'

    def init_reqs(self):
        super().init_reqs()
        self.d.reqs // 'django'

    def init_giti(self):
        super().init_giti()
        self.d.giti.bot // f'/{self}.sqlite*'

    def init_mk(self):
        super().init_mk()
        self.d.mk.all.body.drop() //\
            f'$^ runserver {self.config.HOST}:{self.config.PORT}'
        self.d.mk.alls //\
            (S('migrate: $(PY) $(MODULE).py', pfx='.PHONY: migrate') //
             f'rm {self}.sqlite3' //
             '$^ $@')
        self.d.mk.alls //\
            (S('makemigrations: $(PY) $(MODULE).py', pfx='.PHONY: makemigrations') //
             '$^ $@')
        self.d.mk.alls //\
            (S('createsuperuser: $(PY) $(MODULE).py', pfx='.PHONY: createsuperuser') //
             (S('$^ $@ \\') //
              '--username dponyatov \\' //
              '--email dponyatov@gmail.com'))
        #
        self.d.mk.install.body //\
            '$(MAKE) migrate' //\
            '$(MAKE) createsuperuser'
        #

    def init_py(self):
        super().init_py()
        self.d.py // f'''
import config
import os, sys
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
if __name__ == '__main__':
    main()'''

#######################################################################################


class emModule(dirModule):
    def mixin(self):
        emModule.mixin_giti(self)
        emModule.mixin_mk(self)
        emModule.mixin_apt(self)
        #
        self.d.fw = Dir('firmware')
        self.d // self.d.fw
        self.d.fw.giti = gitiFile()
        self.d.fw // self.d.fw.giti
        self.d.fw.giti.top // '*'
        #
        emModule.mixin_main(self)

    def mixin_giti(self):
        self.d.giti.mid // '*.o'

    def mixin_main(self):
        self.d.src.c = cFile(f'{self}')
        self.d.src // self.d.src.c
        self.d.src.c //\
            f'#include <{self}.h>' //\
            (S('int main() {', '}') //
                (S('while (true) {', '}'))
             ) //\
            (S('void _exit(int c) {', '}') //
                S('while (true) {', '}'))
        self.d.mk.obj.c // f'{"C":<3} += $(SRC)/{self}.c'
        #
        self.d.src.h = hFile(f'{self}')
        self.d.src // self.d.src.h
        self.d.src.h.top //\
            f'#ifndef _H_{self:u}' //\
            f'#define _H_{self:u}'
        self.d.src.h.top //\
            '#include <stdint.h>' //\
            '#include <stdbool.h>'
        self.d.src.h.bot //\
            f'#endif // _H_{self:u}'
        self.d.mk.obj.h // f'{"H":<3} += $(SRC)/{self}.h'
        #
        self.d.mk.obj.s // f'{"S":<3} += $(C) $(H)'

    def mixin_apt(self):
        self.d.apt //\
            'putty'

    def mixin_mk(self):
        self.d.mk.dir //\
            f'{"FW":<9}  = $(CWD)/firmware'
        self.d.mk.tool //\
            f'{"HOSTCC":<9}  = $(CC)' //\
            f'{"CC":<9}  = $(TARGET)-gcc' //\
            f'{"HOSTCXX":<9}  = $(CXX)' //\
            f'{"CXX":<9}  = $(TARGET)-g++' //\
            f'{"LD":<9}  = $(TARGET)-ld' //\
            f'{"AS":<9}  = $(TARGET)-as' //\
            f'{"SIZE":<9}  = $(TARGET)-size' //\
            f'{"OBJDUMP":<9}  = $(TARGET)-objdump' //\
            f'{"GDB":<9}  = $(TARGET)-gdb'
        # CPU
        self.d.cpu = Dir('cpu')
        self.d // self.d.cpu
        #
        self.d.mk.cfg.cflags = Section('cflags')
        self.d.mk.cfg // self.d.mk.cfg.cflags
        self.d.mk.cfg.cflags //\
            f'{"CFLAGS":<9} += -mcpu=$(CPU) $(THUMB)' //\
            f'{"CFLAGS":<9} += -O0 -g3' //\
            f'{"CFLAGS":<9} += -I$(SRC)'
        self.d.mk.obj //\
            f'{"OBJ":<3} += $(FW)/{self}.elf'
        # self.d.mk.all.target // '$(OBJ)'
        # self.d.mk.all.body //\
        #     f'$(MAKE) $(FW)/{self}.elf'
        self.d.mk.rule //\
            (S(f'$(FW)/{self}.elf: $(C) $(H) Makefile') //
             '$(CC) $(CFLAGS) -o $@ $(C)' //
             '$(SIZE) $@' //
             '$(OBJDUMP) -x $@ > $@.objdump'
             )


class stmModule(emModule):
    def mixin(self):
        emModule.mixin(self)
        stmModule.mixin_mk(self)
        stmModule.mixin_apt(self)

    def mixin_mk(self):
        self.d.hw = Dir('hw')
        self.d // self.d.hw
        self.d.hw.pill030 = mkFile('pill030')
        self.d.hw // self.d.hw.pill030
        self.d.hw.pill030 // f'{"SoC":<9}  = STM32F030'
        self.d.hw.pill103 = mkFile('pill103')
        self.d.hw // self.d.hw.pill103
        self.d.hw.pill103 // f'{"SoC":<9}  = STM32F103'
        #
        self.d.mk.var //\
            f'{"HW":<9} ?= pill030' //\
            f'{"include":<9}     hw/$(HW).mk' //\
            f'{"include":<9}    cpu/$(SoC).mk'
        #
        self.d.cpu.cm = mkFile('cortex-m')
        self.d.cpu.cm0 = mkFile('cortex-m0')
        self.d.cpu.cm3 = mkFile('cortex-m3')
        self.d.cpu.cm4 = mkFile('cortex-m4')
        self.d.cpu // self.d.cpu.cm //\
            self.d.cpu.cm0 // self.d.cpu.cm3 // self.d.cpu.cm4
        self.d.cpu.cm //\
            f'{"THUMB":<9}  = -mthumb' //\
            f'{"TARGET":<9}  = arm-none-eabi'
        self.d.cpu.cm0 //\
            f'{"CPU":<9}  = cortex-m0' //\
            f'{"include":<9}    cpu/cortex-m.mk'
        self.d.cpu.cm3 //\
            f'{"CPU":<9}  = cortex-m3' //\
            f'{"include":<9}    cpu/cortex-m.mk'
        self.d.cpu.cm4 //\
            f'{"CPU":<9}  = cortex-m4' //\
            f'{"include":<9}    cpu/cortex-m.mk'
        #
        self.d.cpu.STM32F030 = mkFile('STM32F030')
        self.d.cpu // self.d.cpu.STM32F030
        self.d.cpu.STM32F030 // 'include cpu/cortex-m0.mk'
        self.d.cpu.STM32F103 = mkFile('STM32F103')
        self.d.cpu // self.d.cpu.STM32F103
        self.d.cpu.STM32F103 // 'include cpu/cortex-m3.mk'

    def mixin_apt(self):
        self.d.apt //\
            'gcc-arm-none-eabi gdb-arm-none-eabi openocd' //\
            'stlink-tools stlink-gui'

#######################################################################################


class rsFile(File):
    def __init__(self, V, ext='.rs', comment='//'):
        super().__init__(V, ext, comment)


class Meta(Object):
    pass


class Fn(Meta):
    pass


class rsFn(Fn):
    def file(self, to, depth=0):
        ret = S(f'{to.tab*depth}fn {self.value}() {{', '}')
        for j in self.nest:
            ret // j
        return ret.file(to, depth)


# Rust generic
class rsModule(dirModule):
    def __init__(self, V=None):
        super().__init__(V)
        self.init_rust()

    def init_apt(self):
        super().init_apt()
        self.d.apt // 'curl'

    def init_giti(self):
        super().init_giti()
        self.d.giti.mid // '/target/' // '/Cargo.lock'

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

    def init_mk(self):
        super().init_mk()
        self.d.mk.dir //\
            f'{"CARGOBIN":<9}  = $(HOME)/.cargo/bin'
        self.d.mk.tool //\
            f'{"RUSTUP":<9}  = $(CARGOBIN)/rustup' //\
            f'{"CARGO":<9}  = $(CARGOBIN)/cargo' //\
            f'{"RUSTC":<9}  = $(CARGOBIN)/rustc'
        self.d.mk.all.target // '$(S)'
        self.d.mk.all.body //\
            '$(CARGO) run $(MODULE).ini'
        self.d.mk.install.body //\
            '$(MAKE)   $(RUSTUP)' //\
            '$(RUSTUP) update' //\
            '$(RUSTUP) component add rustfmt'
        self.d.mk.install.post //\
            '$(CARGO)  build'
        self.d.mk.update //\
            '$(RUSTUP) update'
        self.d.mk.install //\
            (S('$(RUSTUP) $(CARGO) $(RUSTC):') //
             "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")

    def init_readme(self):
        super().init_readme()
        self.d.readme.rust = S('### Rust', pfx='\n\n')
        self.d.readme.rust // '''
* [aleksey.kladov](https://www.youtube.com/playlist?list=PLlb7e2G7aSpTfhiECYNI2EZ1uAluUqE_e)
    * [1. Введение (Программирование на Rust)](https://www.youtube.com/watch?v=Oy_VYovfWyo)
    * [2. Время жизни, ADT. Программирование на Rust (весна 2019)](https://www.youtube.com/watch?v=WV-m7xRlXMs)

* [Rust CS196 FA20](https://www.youtube.com/playlist?list=PLddc343N7YqhSPMjlCJa1gRDt4CzjiMYZ)
    * [Welcome to 196! - CS196 FA20](https://www.youtube.com/watch?v=J__JvfNuknU&list=PLddc343N7YqhSPMjlCJa1gRDt4CzjiMYZ&index=1&t=795s)
    * [Rust 1 - Lecture 17 - CS196 FA20](https://www.youtube.com/watch?v=ac7AOtkQMx4)
    * [Rust 2 - Lecture 18 - CS196 FA20](https://www.youtube.com/watch?v=-SKih0Bu7l4)
'''
        self.d.readme // self.d.readme.rust

    def init_cargo(self):
        self.d.cargo = File('Cargo', ext='.toml')
        self.d // self.d.cargo
        #
        self.d.cargo.package = Section('package')
        self.d.cargo //\
            (self.d.cargo.package //
             '[package]' //
             f'{"name":<21}  = "{self:l}"' //
             f'{"version":<21}  = "0.0.1"' //
             f'{"authors":<21}  = ["{self.AUTHOR} <{self.EMAIL}>"]')
        #
        self.d.cargo //\
            f'{"edition":<21}  = "2018"'
        #
        self.d.cargo.dependencies = Section('dependencies')
        self.d.cargo //\
            (self.d.cargo.dependencies //
             '[dependencies]' //
             f'{"lazy_static":<21}  = "*"')

    def init_rust(self):
        self.init_cargo()
        #
        self.d.src.main = rsFile('main')
        self.d.src // self.d.src.main
        self.d.src.main.main = Section('main')
        self.d.src.main //\
            (rsFn('main') // self.d.src.main.main)
        self.d.src.main.top //\
            'use std::env;'
        self.d.src.main.main //\
            (Section('args') //
             'let argv: Vec<String> = env::args().collect();' //
             'let argc = argv.len();' //
             'for i in 0..argc { println!("argv[{}] = {:?}",i,argv[i]); }'
             )


# Rust embedded
class rsemModule(rsModule):

    def __init__(self, V=None):
        super().__init__(V)
        stmModule.mixin(self)
        rsemModule.mixin(self)

    def mixin(self):
        rsemModule.mixin_mk(self)

    def mixin_mk(self):
        self.d.mk.tool //\
            f'{"CC":<9}  = clang --target=$(TARGET)' //\
            f'{"SIZE":<9}  = llvm-size'
        self.d.mk.all.body //\
            '$(CARGO) run $(MODULE).ini'

    def init_apt(self):
        super().init_apt()
        self.d.apt // 'clang clang-tools'

    def init_rust(self):
        assert 1 == 2
        super().init_rust()

    def init_mk(self):
        super().init_mk()
        #
        self.d.mk.all.body.drop()
        self.d.mk.install.body //\
            f'{"$(RUSTUP)":<9} {"component":<9} add llvm-tools-preview'
        # f'{"$(CARGO)":<9} {"install":<9} cargo-binutils' //\

    def init_cargo(self):
        super().init_cargo()
        self.d.cargo.dependencies //\
            f'{"cargo-binutils":<21}  = "*"' //\
            f'{"cortex-m":<21}  = "*"' //\
            f'{"cortex-m-rt":<21}  = "*"' //\
            f'{"cortex-m-semihosting":<21}  = "*"' //\
            f'{"panic-halt":<21}  = "*"' //\
            f'{"nb":<21}  = "*"' //\
            f'{"embedded-hal":<21}  = "*"'

    def init_readme(self):
        super().init_readme()
        self.d.readme.rust // """
### embedded Rust

* [Rust Lang Embedded - Установка и пример (STM32F103C8T6)](https://www.youtube.com/watch?v=IEniVrjncdk)
* https://docs.rust-embedded.org/
    * [The Discovery book](https://docs.rust-embedded.org/discovery/)
    * [The embedded Rust book](https://docs.rust-embedded.org/book/)
"""

    def init_rust(self):
        super().init_rust()


# Rust server
class rsrvModule(rsemModule):

    def init_rust(self):
        super().init_rust()
        self.d.src.main.main //\
            'hello::hello();'
        self.d.src.main.top //\
            'mod hello;'
        self.d.src.main.bot //\
            self.d.src.main.main


#######################################################################################


class exFile(File):
    def __init__(self, V, ext='.ex', comment='#', tab='  '):
        super().__init__(V, ext, comment, tab)


class exsFile(File):
    def __init__(self, V, ext='.exs', comment='#', tab='  '):
        super().__init__(V, ext, comment, tab)


class exModule(dirModule):
    def __init__(self, V=None):
        super().__init__(V)
        self.init_elixir()

    def init_elixir(self):
        self.d.formatter = exsFile('.formatter')
        self.d // self.d.formatter
        self.d.formatter //\
            (S('[', ']') //
             'inputs: ["{mix,.formatter}.exs", "{config,lib,test}/**/*.{ex,exs}"]'
             )
        #
        self.init_elixir_mix()
        self.init_elixir_ex()

    def mixin_web(self):
        webModule.mixin(self)
        self.d.apt // 'nodejs'
        #
        self.d.mix.deps //\
            '{:cowboy, "~> 2.8"},' //\
            '{:plug, "~> 1.11"},' //\
            '{:plug_cowboy, "~> 2.4"},' //\
            '{:ecto, "~> 3.5"},' //\
            '{:json, "~> 1.3"},' //\
            '{:earmark, "~> 1.4"},'
        self.d.mix.application.extra //\
            ':cowboy, :plug,'
        #
        self.d.src.ex.start //\
            f'Logger.info inspect [__MODULE__,__ENV__.function,"http://{self.config.HOST}:{self.config.PORT}" ]' //\
            (S('children = [', ']') //
             (S('{', '}') //
                'Plug.Cowboy, scheme: :http, plug: Web.Router,' //
                f'options: [ip: {self.config.HOST_tuple}, port: {self.config.PORT}]')
             ) //\
            f'opts = [strategy: :one_for_one, name: {self:m}.App]' //\
            'Supervisor.start_link(children, opts)'
        #
        self.d.src.web = Dir('web')
        self.d.src // self.d.src.web
        self.d.src.router = exFile('router')
        self.d.src.web // self.d.src.router
        self.d.mk.obj // f'{"S":<3} += src/web/{self.d.src.router}'
        self.d.src.router //\
            (S('defmodule Web.Router do', 'end') //
             'require Logger' //
             'use Plug.Router' //
             '' //
             'plug Plug.Logger' //
             '' //
             'plug :match' //
             'plug Plug.Static, at: "/static/", from: "static/"' //
             'plug :dispatch' //
             '' //
             (S('defp local,') //
              (S('do: """', '"""', tabs=0) //
               '<a href="/README">README</a>' //
               '#{inspect :calendar.local_time()}' //
               '<hr>')) //
             '' //
             (S('get "/" do', 'end') //
              'conn |> send_resp(:ok,"#{local()} I`m index")') //
             '' //
             (S('get "/css.css" do', 'end') //
              'conn |> send_resp(:ok, File.read!("static/css.css"))') //
             '' //
             (S('get "/favicon.ico" do', 'end') //
              'conn |> send_resp(:ok, File.read!("static/logo.png"))') //
             '' //
             (S('get "/README" do', 'end') //
              'conn' //
              '|> put_resp_content_type("text/html")' //
              '|> send_resp(:ok, local() <> (File.read!("README.md") |> Earmark.as_html!()))') //
             '' //
             (S('match _ do', 'end') //
              'conn' //
              '|> put_resp_content_type("text/plain")' //
              '|> send_resp(:not_found,"""' //
              '#{inspect :calendar.local_time()}' //
              ('-'*66) //
              'conn.request_path: #{inspect conn.request_path}' //
              ('-'*66) //
              '#{inspect conn, limit: :infinity}' //
              '""")') //
             '')

    def init_elixir_ex(self):
        self.d.src.ex = exFile(f'{self:l}')
        self.d.src // self.d.src.ex
        self.d.src.ex.module = Section('module')
        self.d.src.ex.start = Section('start')
        self.d.src.ex.module //\
            'use Application' //\
            (S('def start(_type, _args) do', 'end', pfx='') //
             self.d.src.ex.start)
        self.d.src.ex //\
            (S(f'defmodule {self:m} do', 'end') //
             'require Logger' //
             self.d.src.ex.module //
             (S('def hello do', 'end')//':world'))
        self.d.mk.obj // f'{"S":<3} += src/{self:l}.ex'

    def init_elixir_mix(self):
        self.d.mix = exsFile('mix')
        self.d // self.d.mix
        project = \
            (S('def project do', 'end') //
             (S('[', ']') //
                f'app: :{self:l},' //
                'version: "0.0.1",' //
                'elixir: "~> 1.11",' //
                'elixirc_paths: ["src"],' //
                'start_permanent: Mix.env() == :prod,' //
                'deps: deps()'))
        #
        self.d.mix.application = Section('application')
        self.d.mix.application.extra = Section('extra') // ':logger,'
        self.d.mix.application.mod = Section('mod') // f'mod: {{{self:m}, []}}'
        self.d.mix.application //\
            (S('def application do', 'end') //
             (S('[', ']') //
              (S('extra_applications: [', '],') //
               self.d.mix.application.extra) //
              self.d.mix.application.mod))
        #
        self.d.mix.deps = Section('deps')
        deps = (S('defp deps do', 'end') //
                (S('[', ']') //
                 self.d.mix.deps //
                 '{:exsync, "~> 0.2.4", only: :dev},'
                 ))
        #
        self.d.mix //\
            (S(f'defmodule {self:m}.MixProject do', 'end') //
             'use Mix.Project' //
             project //
             self.d.mix.application //
             deps //
             '')

    def init_mk(self):
        super().init_mk()
        self.d.mk.tool // f'{"MIX":<9}  = mix' // f'{"IEX":<9}  = iex'
        self.d.mk.obj // f'{"S":<3} += mix.exs'
        self.d.mk.all.target // '$(S)'
        self.d.mk.all.body //\
            '$(MIX)  format $(S)' //\
            '$(IEX)  -S $(MIX)' //\
            '$(MAKE) $@'
        self.d.mk.update // '$(MIX) deps.get'
        self.d.mk.merge // 'MERGE += .formatter.exs mix.exs'

    def init_apt(self):
        super().init_apt()
        self.d.apt // 'erlang elixir'

    def init_giti(self):
        super().init_giti()
        self.d.giti.mid //\
            '/_build/' //\
            '/cover/' //\
            '/deps/' //\
            'erl_crash.dump' //\
            '/mix.lock'

    def init_vscode_settings(self):
        super().init_vscode_settings()
        s = S() //\
            '"**/_build/**": true, "**/.elixir_ls/**": true,' //\
            '"**/deps/**": true,' //\
            '"**/.formatter.exs": true, "**/mix.lock": true,'
        self.d.vscode.settings.watcher // s
        self.d.vscode.settings.exclude // s
        self.d.vscode.settings.f12.value = 'System.stop'

    def init_vscode_extensions(self):
        super().init_vscode_extensions()
        self.d.vscode.extensions // '"jakebecker.elixir-ls",'

    def init_readme(self):
        super().init_readme()
        self.d.readme.erlang = (S('\n\n### Erlang / Elixir'))
        self.d.readme // self.d.readme.erlang
        self.d.readme.erlang // '''
* [Elixir - как без усилий поднять тысячи процессов на одной машине](https://www.youtube.com/watch?v=jmW5ngfYmdc)
* [Elixir School /ru/](https://elixirschool.com/ru/) — главный ресурс для тех, кто хочет изучить язык программирования Elixir.
* [ElixirBridge /en/](http://elixirbridge.org/docs/)

#### BEAM virtual machine

* [The BEAM Book](https://github.com/happi/theBeamBook)
* embedded/alternate Erlang VMs:
  * https://github.com/bettio/AtomVM
  * https://github.com/kvakvs/E4VM
  * [Erlang on Microcontrollers: The Research Continues - Dmytro Lytovchenko - EUC17](https://www.youtube.com/watch?v=6NUPormxgw8)

#### Books

* Саша Юрич [Elixir в действии](https://dmkpress.com/catalog/computer/programming/functional/978-5-97060-773-2/)
* Чезарини Ф. [Программирование в Erlang](https://dmkpress.com/catalog/computer/programming/functional/978-5-94074-617-1/)
* Чезарини Франческо, Виноски Стивен [Проектирование масштабируемых систем с помощью Erlang/OTP](https://www.ozon.ru/context/detail/id/140152220/)

#### Databases

* `Ecto`
    * [ElixirConf 2017 - Thinking In Ecto - Darin Wilson](https://www.youtube.com/watch?v=YQxopjai0CU)
    * [Working with Ecto and Postgres](https://www.youtube.com/playlist?list=PLFhQVxlaKQEmRRHyX5LBl9TLSLGRzdyFq)

#### Web

* `Cowboy` pure web server
    * [Building Alchemist.Camp](https://www.youtube.com/playlist?list=PLFhQVxlaKQEn5pqhwqdxItvv80ZnoLqMA)

* `Plug` composable web module specification
    * Tensor Programming [Elixir Tutorial Part 5 (Plug and Cowboy)](https://www.youtube.com/watch?v=F4oAZx_ao4s)
    * [Building a Static Site in Elixir](https://www.youtube.com/watch?v=CK78zms9IHM)
    * [Elixir: Setup Plug and Cowboy - 004](https://www.youtube.com/watch?v=VxepM7_54dA)
'''

#######################################################################################


class cFile(File):
    def __init__(self, V, ext='.c', comment='/*'):
        super().__init__(V, ext, comment)


class hFile(cFile):
    def __init__(self, V, ext='.h'):
        super().__init__(V, ext)


class cppFile(cFile):
    def __init__(self, V, ext='.cpp', comment='//'):
        super().__init__(V, ext, comment)


class lexFile(File):
    def __init__(self, V, ext='.lex', comment='/*'):
        super().__init__(V, ext, comment)


class yaccFile(File):
    def __init__(self, V, ext='.yacc', comment='/*'):
        super().__init__(V, ext, comment)


class cModule(dirModule):
    def init_apt(self):
        super().init_apt()
        self.d.apt // 'build-essential tcc'

    def init_mk(self):
        super().init_mk()
        #
        self.d.mk.tool //\
            f'{"CC":<9}  = tcc'
        #
        self.d.mk.cfg //\
            'CFLAGS += -O0 -g2'
        #
        self.d.mk.rule //\
            (S('$(BIN)/%: $(SRC)/%.c')//'$(CC) $(CFLAGS) -o $@ $<')


class cppModule(cModule):
    def init_apt(self):
        super().init_apt()
        self.d.apt // 'g++'

    def init_mk(self):
        super().init_mk()
        self.d.mk.tool //\
            f'{"CXX":<9}  = g++'
        #
        self.d.mk.rule //\
            (S('$(BIN)/%: $(SRC)/%.cpp')//'$(CXX) $(CFLAGS) -o $@ $<')

#######################################################################################


class Import(Meta):
    def file(self, to, depth=0):
        return f'import {self}\n'


class Class(Meta):
    def __init__(self, V, sup=[]):
        super().__init__(V)
        for s in sup:
            self // s

    def file(self, to, depth=0):
        ret = f'class {self}'
        if not self.nest:
            ret += ': pass\n'
        else:
            ret += '('
            ret += ','.join(map(lambda s: f'{s.value}', self.nest))
            ret += '): pass\n'
        return ret


class circularModule(pyModule):

    def init_reqs(self):
        super().init_reqs()
        self.d.reqs // 'ply' // 'xxhash'

    def init_vscode_settings(self):
        super().init_vscode_settings()
        self.d.vscode.settings.f11.value = ' make pep '
        self.d.vscode.settings.f12.value = f' clear ; make '

    def init_py(self):
        super().init_py()
        #
        self.d.py.imports = Section('imports')
        self.d.py // self.d.py.imports
        for i in ['os', 'sys', 're']:
            self.d.py.imports // Import(i)
        #
        self.c = Section('classtree')
        #
        self.d.py.object = Section('executable graph object')
        self.d.py // self.d.py.object
        self.c.object = Class('Object')
        self.d.py.object // self.c.object
        #
        self.d.py.primitive = Section('primitives')
        self.d.py // self.d.py.primitive
        self.c.primitive = Class('Primitive', [self.c.object])
        self.d.py.primitive // self.c.primitive
        self.c.name = Class('Name', [self.c.primitive])
        self.d.py.primitive // self.c.name
        self.c.string = Class('String', [self.c.primitive])
        self.d.py.primitive // self.c.string
        self.c.number = Class('Number', [self.c.primitive])
        self.d.py.primitive // self.c.number
        self.c.integer = Class('Integer', [self.c.number])
        self.d.py.primitive // self.c.integer
        self.c.hex = Class('Hex', [self.c.integer])
        self.d.py.primitive // self.c.hex
