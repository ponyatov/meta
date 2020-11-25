# \ <section:var>
MODULE  = $(notdir $(CURDIR))
OS      = $(shell uname -s)
MACHINE = $(shell uname -m)
# / <section:var>
# \ <section:dir>
CWD     = $(CURDIR)
DOC     = $(CWD)/doc
BIN     = $(CWD)/bin
SRC     = $(CWD)/src
TMP     = $(CWD)/tmp
# / <section:dir>
# \ <section:tool>
WGET    = wget -c
CARGO   = $(shell which cargo)
RUSTC   = $(shell which rustc)
# / <section:tool>
# \ <section:all>
.PHONY: all
all:
	$(CARGO) run
# / <section:all>
# \ <section:install>
.PHONY: install
install: $(OS)_install
	# \ <section:install>
	$(CARGO) build
	# / <section:install>
.PHONY: update
update: $(OS)_update
.PHONY: $(OS)_install $(OS)_update
$(OS)_install $(OS)_update:
	sudo apt update
	sudo apt install -u `cat apt.txt`
# / <section:install>
