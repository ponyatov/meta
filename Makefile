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
S += bully.py
S += SCADA.py
S += FORTH.py
S += circ.py
S += meteo.py
S += elixirbook.py
S += incremento.py
S += rustpill.py
#S

.PHONY: pep
pep: $(PEP) $(S)
	$(PEP) --in-place $(S)

flOwS: $(PY) $(S)
	$(PY) flOwS.py

bully: $(PY) $(S)
	$(PY) bully.py

SCADA: $(PY) $(S)
	$(PY) SCADA.py

FORTH: $(PY) $(S)
	$(PY) FORTH.py

circ: $(PY) $(S)
	$(PY) circ.py

meteo: $(PY) $(S)
	$(PY) meteo.py

elixirbook: $(PY) $(S)
	$(PY) elixirbook.py

incremento: $(PY) $(S)
	$(PY) incremento.py

rustpill: $(PY) $(S)
	$(PY) rustpill.py
#M

$(PY) $(PIP):
	python3 -m venv .
	$(PIP) install -U pip autopep8
	$(PIP) install -U -r requirements.pip
