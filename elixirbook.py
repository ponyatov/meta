
from metaL import *


class texFile(File):
    def __init__(self, V, ext='.tex', comment='%'):
        super().__init__(V, ext, comment)


class texModule(dirModule):
    def __init__(self, V=None):
        super().__init__(V)
        self.init_tex()

    def init_mk(self):
        super().init_mk()
        self.d.mk.tool //\
            f'{"LATEX":<9} = pdflatex -halt-on-error --output-dir=$(TMP)'
        self.d.mk.obj //\
            f'TEX += tex/{self}.tex tex/header.tex'
        self.d.mk.all.body // '$(MAKE) pdf'
        self.d.mk.alls //\
            (S(f'pdf: $(DOC)/{self}.pdf', pfx='.PHONY: pdf')) //\
            (S(f'$(DOC)/{self}.pdf: $(TMP)/{self}.pdf') //
                'cp $< $@') //\
            (S(f'$(TMP)/{self}.pdf: $(TEX)') //
                f'cd tex ; $(LATEX) {self}')

    def init_vscode_extensions(self):
        super().init_vscode_extensions()
        self.d.vscode.extensions //\
            '"james-yu.latex-workshop",' //\
            '"yzane.markdown-pdf",'
            # '"tomoki1207.pdf",'

    def init_tex(self):
        self.d.tex = Dir('tex')
        self.d // self.d.tex
        #
        self.d.tex.header = texFile(f'header')
        self.d.tex // self.d.tex.header
        self.d.tex.header // r"""
% Universal LaTeX header for e-book publications
\documentclass[oneside,10pt]{book}
%% mobile phone optimized
%%% honor 3C 108 mm x 62 mm scaled 1.1 = 118.8 x 68.2
\usepackage[paperwidth=118.8mm,paperheight=68.2mm,margin=2mm]{geometry}
%% font setup for screen reading
\renewcommand{\familydefault}{\sfdefault}\normalfont
%% hyperlinks pdf style
\usepackage[unicode,colorlinks=true,linkcolor=green,urlcolor=blue]{hyperref}
%% fix heading styles for tiny paper
\usepackage{titlesec}
\titleformat{\chapter}{\Large\bfseries}{\thechapter.}{1em}{}
\titleformat{\section}{\large\bfseries}{\thesection.}{1em}{}
"""
        self.d.tex.header // r"""
% xcolor fixes
\usepackage{xcolor}
\definecolor{red  }{rgb}{0.3, 0 , 0 }	% G
\definecolor{green}{rgb}{ 0 ,0.3, 0 }	% G
\definecolor{blue }{rgb}{ 0 , 0 ,0.3}	% B
"""
        self.d.tex.header // r"""
% Cyrillization
%% \usepackage[T1,T2A]{fontenc}
\usepackage[utf8]{inputenc}
%% \usepackage[cp1251]{inputenc}
\usepackage[english,russian]{babel}
\usepackage{indentfirst}        
"""
        self.d.tex.header // r"""
% misc
\newcommand{\email}[1]{$<$\href{mailto:#1}{#1}$>$}
"""
        self.d.tex.header // r"""
\usepackage{titling}
"""
        #
        self.d.tex.main = texFile(f'{self}')
        self.d.tex // self.d.tex.main
        self.d.tex.main //\
            '\\input{header}'
        self.d.tex.main //\
            f'\\title{{{self.TITLE}}}' //\
            f'\\author{{\\copyright\\ {self.AUTHOR} \\email{{{self.EMAIL}}}}}' //\
            r'\date{\today}'
        self.d.tex.main //\
            (S('\\begin{document}', '\\end{document}') // r"""
        \ \\
        
        {\LARGE \thetitle}

        \ \\

        \theauthor
        
        \ \\
        
        \thedate
"""//\

             r'\tableofcontents' //
             r'\input{intro}'
             )


class thisModule(texModule):
    def __init__(self, V=None):
        super().__init__(V)


mod = thisModule()
mod.TITLE = 'Язык Elixir (Erlang) для веб-разработчика'
mod.init_tex()
mod.ABOUT = """
черновик книги
"""

mod.d.mk.obj // 'TEX += tex/intro.tex'

sync()
