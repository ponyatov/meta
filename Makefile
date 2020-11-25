MODULE = $(notdir $(CURDIR))
OS = $(shell uname -s)
MACHINE = $(shell uname -m)

CWD = $(CURDIR)

PY = $(CWD)/bin/python3
PIP = $(CWD)/bin/pip3
PEP = $(CWD)/bin/autopep8

S += metaL.py
S += bully.py
S += ./do
S += flOwS.py
#S

.PHONY: pep
pep: $(PEP) $(S)
	$(PEP) --in-place $(S)

bully: $(PY) $(S)
	$(MAKE) pep
	$(PY) bully.py

flOwS: $(PY) $(S)
	$(PY) flOwS.py
#M

$(PY) $(PIP):
	python3 -m venv .
	$(PIP) install -U pip autopep8
