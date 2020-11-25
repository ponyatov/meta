MODULE = $(notdir $(CURDIR))
OS = $(shell uname -s)
MACHINE = $(shell uname -m)

CWD = $(CURDIR)

PY = $(CWD)/bin/python3
PIP = $(CWD)/bin/pip3
PEP = $(CWD)/bin/autopep8

S += metaL.py
S += bully.py

bully: $(PY) $(S)
	$(PEP) -i bully.py
	$(PY) bully.py

$(PY) $(PIP):
	python3 -m venv .
	$(PIP) install -U pip autopep8
