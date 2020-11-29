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
CC        = tcc
CXX       = g++
# / <section:tool>
# \ <section:obj>
BINS += $(BIN)/vm $(BIN)/compiler
BC   += $(TMP)/$(MODULE).bc
# / <section:obj>
# \ <section:cfg>
CFLAGS += -O0 -g2
# / <section:cfg>
# \ <section:all>
# \ <section:all>
.PHONY: all
all: $(BINS) $(BC)	
	$(BIN)/vm $(TMP)/FORTH.bc
# / <section:all>
# / <section:all>
# \ <section:rules>
$(BIN)/%: $(SRC)/%.c
	$(CC) $(CFLAGS) -o $@ $<
$(BIN)/%: $(SRC)/%.cpp
	$(CXX) $(CFLAGS) -o $@ $<
$(TMP)/%.bc: $(BIN)/compiler $(SRC)/%.4th
	$^ $@
# / <section:rules>
# \ <section:install>
.PHONY: install
install: $(OS)_install
.PHONY: update
update: $(OS)_update
.PHONY: $(OS)_install $(OS)_update
$(OS)_install $(OS)_update:
	sudo apt update
	sudo apt install -u `cat apt.txt`
# / <section:install>
# \ <section:merge>
MERGE  = Makefile README.md apt.txt .gitignore .vscode $(S)
# / <section:merge>
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
