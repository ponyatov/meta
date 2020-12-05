# \ <section:var>
MODULE     = $(notdir $(CURDIR))
OS         = $(shell uname -s)
MACHINE    = $(shell uname -m)
NOW        = $(shell date +%d%m%y)
REL        = $(shell git rev-parse --short=4 HEAD)
# / <section:var>
# \ <section:dir>
CWD        = $(CURDIR)
DOC        = $(CWD)/doc
BIN        = $(CWD)/bin
SRC        = $(CWD)/src
TMP        = $(CWD)/tmp
# / <section:dir>
# \ <section:tool>
WGET       = wget -c
PY         = $(BIN)/python3
PIP        = $(BIN)/pip3
PEP        = $(BIN)/autopep8
PYT        = $(BIN)/pytest
# / <section:tool>
# \ <section:obj>
S += ./do metaL.py
S += circ.py
S += SCADA.py
S += flOwS.py
S += rustpill.py
S += meteo.py
S += elixirbook.py
S += bully.py
#S
# / <section:obj>
# \ <section:all>
.PHONY: all
all: $(PY)	
.PHONY: pep
pep: $(PEP) $(S)
	$(PEP) --in-place $(S)

circ: $(PY) $(S)
	$(PY) circ.py

SCADA: $(PY) $(S)
	$(PY) SCADA.py

flOwS: $(PY) $(S)
	$(PY) flOwS.py

rustpill: $(PY) $(S)
	$(PY) rustpill.py

meteo: $(PY) $(S)
	$(PY) meteo.py

elixirbook: $(PY) $(S)
	$(PY) elixirbook.py

bully: $(PY) $(S)
	$(PY) bully.py
#M
# / <section:all>
# \ <section:install>
.PHONY: install
install: $(OS)_install
	# \ <section:body>
	$(MAKE) $(PIP)
	$(MAKE) update
	# / <section:body>
.PHONY: update
update: $(OS)_update
	# \ <section:update>
	$(PIP) install -U pip autopep8
	$(PIP) install -U -r requirements.pip
	# / <section:update>
.PHONY: $(OS)_install $(OS)_update
$(OS)_install $(OS)_update:
	sudo apt update
	sudo apt install -u `cat apt.txt`
# \ <section:pyinst>
$(PY) $(PIP):
	python3 -m venv .
	$(MAKE) update
# / <section:pyinst>
# / <section:install>
# \ <section:merge>
MERGE  = Makefile README.md apt.txt .gitignore .vscode $(S)
.PHONY: main
main:
.PHONY: shadow
shadow:
.PHONY: release
release:
# / <section:merge>
