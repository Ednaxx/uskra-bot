UNAME := $(shell uname)

default:
	echo "See README.md"

ifeq ($(OS), Windows_NT)
init: windows_init
run: windows_run
else
init: linux_init
run: linux_run
endif

linux_init:
	python3 -m venv .venv; \
	. .venv/bin/activate; \
	pip install -r requirements.txt; \

linux_run:
	. .venv/bin/activate; \
	python ./uskra_bot/app.py; \


windows_init:
	python -m venv .venv; \
	source .venv/Scripts/activate; \
	pip install -r requirements.txt; \

windows_run:
	source .venv/Scripts/activate; \
	python ./uskra_bot/app.py; \
