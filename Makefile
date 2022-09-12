#* Variables
SHELL := /usr/bin/env bash

# If virtualenv exists, use it. If not, use PATH to find
SYSTEM_PYTHON  = $(or $(shell which python3), $(shell which python))
PYTHON         = $(or $(wildcard venv/bin/python), $(SYSTEM_PYTHON))

## Environment
venv:
	rm -rf venv
	$(SYSTEM_PYTHON) -m venv venv

deps:
	$(PYTHON) -m pip install --upgrade pip -r requirements.txt

## Build
pkgs:
	python bin/build.py
