
# This file is based on a Make file found under https://github.com/StackStorm/st2contrib/blob/c89c568a97e26ee70fc44e2cf19450e4494038e4/Makefile
# This is licensed under Apache License 2.0, and changes have been made to adopt it to only run tests in this
# repo.

ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
VIRTUALENV_DIR ?= virtualenv
ST2_REPO_PATH ?= /tmp/st2
ST2_REPO_BRANCH ?= master

export ST2_REPO_PATH ROOT_DIR

# All components are prefixed by st2
COMPONENTS := $(wildcard /tmp/st2/st2*)

.PHONY: all
all: requirements packs-resource-register packs-tests

.PHONY: packs-resource-register
packs-resource-register: requirements .mkpacksdir .clone_st2_repo .packs-resource-register

.PHONY: packs-tests
packs-tests: requirements .clone_st2_repo .packs-tests

.PHONY: .packs-resource-register
.packs-resource-register:
	@echo
	@echo "==================== packs-resource-register ===================="
	@echo
	. $(VIRTUALENV_DIR)/bin/activate; st2-check-register-pack-resources $(PWD)

.PHONY: .packs-tests
.packs-tests:
	@echo
	@echo "==================== packs-tests ===================="
	@echo
	. $(VIRTUALENV_DIR)/bin/activate; $(ST2_REPO_PATH)/st2common/bin/st2-run-pack-tests -x -p $(PWD)

.PHONY: .clone_st2_repo
.clone_st2_repo:
	@echo
	@echo "==================== cloning st2 repo ===================="
	@echo
	@rm -rf /tmp/st2
	@git clone https://github.com/StackStorm/st2.git --depth 1 --single-branch --branch $(ST2_REPO_BRANCH) /tmp/st2

.PHONY: requirements
requirements: virtualenv
	@echo
	@echo "==================== requirements ===================="
	@echo
	. $(VIRTUALENV_DIR)/bin/activate && $(VIRTUALENV_DIR)/bin/pip install --upgrade pip
	. $(VIRTUALENV_DIR)/bin/activate && $(VIRTUALENV_DIR)/bin/pip install --cache-dir $(HOME)/.pip-cache -q -r requirements.txt
	. $(VIRTUALENV_DIR)/bin/activate && $(VIRTUALENV_DIR)/bin/pip install --cache-dir $(HOME)/.pip-cache -q -r requirements-test.txt
	# Note: Line below is a work around for corrupted Travis Python wheel cache issue
	. $(VIRTUALENV_DIR)/bin/activate && $(VIRTUALENV_DIR)/bin/pip install --no-cache-dir --no-binary :all: --upgrade --force-reinstall greenlet

.PHONY: virtualenv
virtualenv: $(VIRTUALENV_DIR)/bin/activate
$(VIRTUALENV_DIR)/bin/activate:
	@echo
	@echo "==================== virtualenv ===================="
	@echo
	test -d $(VIRTUALENV_DIR) || virtualenv --no-site-packages $(VIRTUALENV_DIR)

.PHONY: .mkpacksdir
.mkpacksdir:
	@echo
	@echo "==================== (Hack) create a packs dir linking back to source to allow for packs-registration ===================="
	@echo
	if [ ! -L packs/arteria-packs ]; then mkdir -p packs && ln -s $(PWD) packs/arteria-packs; fi
