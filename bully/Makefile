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
S   += $(MODULE).py
# / <section:obj>
# \ <section:all>
.PHONY: all
all: $(PY) $(MODULE).py	
	# \ <section:body>
	$^ runserver 127.0.0.1:35472
	# / <section:body>
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
# \ <section:install>
.PHONY: install
install: $(OS)_install
	# \ <section:body>
	$(MAKE) $(PIP)
	$(MAKE) update
	$(MAKE) migrate
	$(MAKE) createsuperuser
	$(MAKE) js
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
# \ <section:js>
.PHONY: js
js: \
	static/jquery.js \
	static/bootstrap.css static/bootstrap.js \
	static/html5shiv.js static/respond.js \
	static/leaflet.css static/leaflet.js

JQUERY_VER = 3.5.1
JQUERY_JS  = https://code.jquery.com/jquery-$(JQUERY_VER).min.js
static/jquery.js:
	$(WGET) -O $@ $(JQUERY_JS)

BOOTSTRAP_VER = 3.4.1
static/bootstrap.css:
	$(WGET) -O $@ https://bootswatch.com/3/darkly/bootstrap.min.css
static/bootstrap.js:
	$(WGET) -O $@ https://maxcdn.bootstrapcdn.com/bootstrap/$(BOOTSTRAP_VER)/js/bootstrap.min.js

HTML2SHIV_VER = 3.7.3
HTML2SHIV_URL = https://cdnjs.cloudflare.com/ajax/libs/html5shiv/$(HTML2SHIV_VER)/html5shiv-printshiv.min.js
static/html5shiv.js:
	$(WGET) -O $@ $(HTML2SHIV_URL)

RESPOND_VER = 1.4.2
RESPOND_URL = https://cdnjs.cloudflare.com/ajax/libs/respond.js/$(RESPOND_VER)/respond.min.js
static/respond.js:
	$(WGET) -O $@ $(RESPOND_URL)

LEAFLET_VER = 1.7.1
LEAFLET_ZIP = http://cdn.leafletjs.com/leaflet/v$(LEAFLET_VER)/leaflet.zip
$(TMP)/leaflet.zip:
	$(WGET) -O $@ $(LEAFLET_ZIP)
static/leaflet.css: static/leaflet.js
static/leaflet.js: $(TMP)/leaflet.zip
	unzip -d static $< leaflet.css leaflet.js* images/* && touch $@
# / <section:js>
# / <section:install>
# \ <section:merge>
MERGE  = Makefile README.md apt.txt .gitignore .vscode $(S)
.PHONY: main
main:
	git push -v
	git checkout $@
	git pull -v
	git checkout shadow -- $(MERGE)
.PHONY: shadow
shadow:
	git pull -v
	git checkout $@
	git pull -v
.PHONY: release
release:
	git tag $(NOW)-$(REL)
	git push -v && git push -v --tags
	$(MAKE) shadow
MERGE += static templates
# / <section:merge>
