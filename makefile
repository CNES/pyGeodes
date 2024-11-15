POETRY = poetry
RUN = $(POETRY) run

.PHONY: list

list:
	@LC_ALL=C $(MAKE) -pRrq -f $(firstword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep -E -v -e '^[^[:alnum:]]' -e '^$@$$'

format:
	$(RUN) black -l 80 .

lint_source:
	$(RUN) flake8 --ignore=E501,F541  pygeodes/

lint_tests:
	$(RUN) flake8 tests/

build:
	$(POETRY) build

full_build:
	$(RUN) python3 utils/copy_info.py
	$(POETRY) build

test:
	$(RUN) python3 -m unittest discover tests

test_utils:
	$(RUN) python3 -m unittest discover tests/utils/
    
build_docs:
	rm -rf docs/build/*
	$(RUN) sphinx-apidoc -o ./docs/source pygeodes/
	$(RUN) sphinx-build -M html ./docs/source ./docs/build
	
publish:
	twine upload -r local dist/*