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
        raise TypeError(spec)

    ######################################################################

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

#######################################################################################


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

    def __init__(self, V, ext='', comment='#', tab=' '*4):
        super().__init__(f'{V}{ext}')
        #
        self.ext = ext
        self.tab = tab
        self.comment = comment
        self.commend = ''
        if self.comment == '/*':
            self.commend = ' */'
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
    def __init__(self, V='Makefile', ext='', comment='#',  tab='\t'):
        super().__init__(V, ext, comment, tab)


class jsonFile(File):
    def __init__(self, V, ext='.json', comment='/*'):
        super().__init__(V, ext, comment)

#######################################################################################


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
                 '"tabnine.tabnine-vscode",' //
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
        self.d.mk.alls = Section('all')
        self.d.mk // self.d.mk.alls
        self.d.mk.all = Section('all')
        self.d.mk.alls // self.d.mk.all
        self.d.mk.all.target = S(' ', inline=True)
        self.d.mk.all.body = S()
        self.d.mk.all //\
            (S('all:', pfx='.PHONY: all', inline=True) //
             self.d.mk.all.target) //\
            (self.d.mk.all.body)
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
            f'{"PY":<9} = $(BIN)/python3' //\
            f'{"PIP":<9} = $(BIN)/pip3' //\
            f'{"PEP":<9} = $(BIN)/autopep8' //\
            f'{"PYT":<9} = $(BIN)/pytest'
        #
        self.d.mk.obj // 'S += $(MODULE).py'
        #
        self.d.mk.all.target // '$(PY) $(MODULE).py'
        self.d.mk.all.body // '$^'
        #
        self.d.mk.alls //\
            (S('pep: $(PEP) $(S)', pfx='.PHONY: pep') //
                '$(PEP) --in-place $(S)')
        #
        self.d.mk.pyinst = Section('pyinst')
        self.d.mk.inst // self.d.mk.pyinst
        self.d.mk.install //\
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
            '/bin' //\
            '/lib' //\
            '/lib64' //\
            '/share' //\
            '__pycache__' //\
            '/pyvenv.cfg'

    def init_vscode_settings(self):
        super().init_vscode_settings()
        pyfiles = re.sub(r'^\s+', '', '''
        "**/__pycache__/**": true,
        "**/bin/**": true, "**/include/**": true, "**/lib*/**": true,
        "**/share/**": true, "**/*.pyc": true, "**/pyvenv.cfg": true,''')
        self.d.vscode.settings.watcher // pyfiles
        self.d.vscode.settings.exclude // pyfiles
        self.d.vscode.settings.assoc //\
            '"**/*.py": "python",' // '"requirements.*": "config",'

#######################################################################################

class cssFile(File):
    def __init__(self, V,ext='.css', comment='/*'):
        super().__init__(V, ext, comment)

class webModule(pyModule):
    def __init__(self, V=None):
        super().__init__(V)
        self.init_static()
        self.init_templates()

    def init_static(self):
        self.d.static = Dir('static')
        self.d // self.d.static
        self.d.static // File('.gitignore')
        #
        self.d.static.css = cssFile('css')
        self.d.static // self.d.static.css

    def init_templates(self):
        self.d.templates = Dir('templates')
        self.d // self.d.templates
        self.d.templates // File('.gitignore')


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
            "STATIC_URL = '/static/'"
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
            "LANGUAGE_CODE = 'ru-ru'"

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
        self.d.mk.install //\
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


class rsModule(dirModule):
    def __init__(self, V=None):
        super().__init__(V)
        self.init_rust()

    def init_rust(self):
        self.init_cargo()
        self.d.src.main = rsFile('main')
        self.d.src // self.d.src.main
        self.d.src.main.main = \
            (rsFn('main') //
             '//' //
             'let argv: Vec<String> = env::args().collect();' //
             'let argc = argv.len();' //
             'for i in 0..argc { println!("argv[{}] = {:?}",i,argv[i]); }' //
             '//' //
             'hello::hello();'
             )
        self.d.src.main.top //\
            'use std::env;'
        self.d.src.main.top //\
            'mod hello;'
        self.d.src.main.bot //\
            self.d.src.main.main

    def init_giti(self):
        super().init_giti()
        self.d.giti.mid // '/target/' // '/Cargo.lock'

    def init_apt(self):
        super().init_apt()
        self.d.apt // 'curl'

    def init_readme(self):
        super().init_readme()
        self.d.readme.rust = S('### Rust', pfx='')
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

    def init_mk(self):
        super().init_mk()
        self.d.mk.dir //\
            f'{"CARGOBIN":<9} = $(HOME)/.cargo/bin'
        self.d.mk.tool //\
            f'{"RUSTUP":<9} = $(CARGOBIN)/rustup' //\
            f'{"CARGO":<9} = $(CARGOBIN)/cargo' //\
            f'{"RUSTC":<9} = $(CARGOBIN)/rustc'
        self.d.mk.all.target // '$(S)' // '$(MODULE).ini'
        self.d.mk.all.body //\
            '$(CARGO) run $(MODULE).ini'
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
             f'{"authors":<9} = ["{self.AUTHOR} <{self.EMAIL}>"]')
        #
        self.d.cargo //\
            f'{"edition":<9} = "2018"'
        #
        self.d.cargo.dependencies = Section('dependencies')
        self.d.cargo //\
            (self.d.cargo.dependencies //
             '[dependencies]' //
             'lazy_static = ""')


class iniFile(File):
    def __init__(self, V, ext='.ini', comment='#'):
        super().__init__(V, ext, comment)
