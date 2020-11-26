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
CARGOBIN  = $(HOME)/.cargo/bin
# / <section:dir>
# \ <section:tool>
WGET      = wget -c
RUSTUP    = $(CARGOBIN)/rustup
CARGO     = $(CARGOBIN)/cargo
RUSTC     = $(CARGOBIN)/rustc
# / <section:tool>
# \ <section:all>
.PHONY: all
all:
	$(CARGO) run
# / <section:all>
# \ <section:inst>
.PHONY: install
install: $(OS)_install
	# \ <section:install>
	$(MAKE)   $(RUSTUP)
	$(RUSTUP) update
	$(RUSTUP) component add rustfmt
	$(CARGO)  build
	# / <section:install>
.PHONY: update
update: $(OS)_update
	# \ <section:update>
	$(RUSTUP) update
	# / <section:update>
.PHONY: $(OS)_install $(OS)_update
$(OS)_install $(OS)_update:
	sudo apt update
	sudo apt install -u `cat apt.txt`
$(RUSTUP) $(CARGO) $(RUSTC):
	curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
# / <section:inst>
