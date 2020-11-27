# \ <section:var>
MODULE    = $(notdir $(CURDIR))
OS        = $(shell uname -s)
MACHINE   = $(shell uname -m)
# / <section:var>
# \ <section:dir>
CWD       = $(CURDIR)
DOC       = $(CWD)/doc
BIN       = $(CWD)/bin
SRC       = $(CWD)/src
TMP       = $(CWD)/tmp
# / <section:dir>
# \ <section:tool>
WGET      = wget -c
PY        = $(BIN)/python3
PIP       = $(BIN)/pip3
PEP       = $(BIN)/autopep8
PYT       = $(BIN)/pytest
# / <section:tool>
# \ <section:obj>
S += $(MODULE).py
# / <section:obj>
# \ <section:all>
# \ <section:all>
.PHONY: all
all: $(PY) $(MODULE).py
	$^ runserver 127.0.0.1:35472
# / <section:all>
.PHONY: pep
pep: $(PEP) $(S)
	$(PEP) --in-place $(S)
.PHONY: migrate
migrate: $(PY) $(MODULE).py
	rm bully.sqlite3
	$^ $@
.PHONY: makemigrations
makemigrations: $(PY) $(MODULE).py
	$^ $@
.PHONY: createsuperuser
createsuperuser: $(PY) $(MODULE).py
	$^ $@ \
		--username dponyatov \
		--email dponyatov@gmail.com
# / <section:all>
# \ <section:inst>
.PHONY: install
install: $(OS)_install
	# \ <section:install>
	$(MAKE) $(PIP)
	$(MAKE) update
	$(MAKE) migrate
	$(MAKE) createsuperuser
	# / <section:install>
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
# / <section:inst>
