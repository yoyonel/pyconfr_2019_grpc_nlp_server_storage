# https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html
.PHONY: clean clean-build clean-pyc help
# https://www.gnu.org/software/make/manual/html_node/Special-Variables.html
.DEFAULT_GOAL := help

PROJECT_NAME?=pyconfr_2019_grpc_nlp_protos
#
PACKAGE_NAME=$(shell python setup.py --name)
PACKAGE_FULLNAME=$(shell python setup.py --fullname)
PACKAGE_VERSION:=$(shell python setup.py --version | tr + _)
#
DOCKER_USER?=yoyonel
DOCKER_TAG?=$(DOCKER_USER)/$(PROJECT_NAME):${PACKAGE_VERSION}
#
PYPI_SERVER?=https://test.pypi.org/simple/
PYPI_SERVER_FOR_UPLOAD?=pypitest
PYPI_CONFIG_FILE?=${HOME}/.pypirc
PYPI_REGISTER?=
# https://stackoverflow.com/questions/2019989/how-to-assign-the-output-of-a-command-to-a-makefile-variable
PYPI_SERVER_HOST=$(shell echo $(PYPI_SERVER) | sed -e "s/[^/]*\/\/\([^@]*@\)\?\([^:/]*\).*/\2/")
PYTEST_OPTIONS?=-v
#
TOX_DIR?=${HOME}/.tox/$(PROJECT_NAME)
#
SDIST_PACKAGE=dist/${shell python setup.py --fullname}.tar.gz
SOURCES=$(shell find src/ -type f -name '*.py') setup.py MANIFEST.in
PROTOS=$(shell find src/ -type f -name '*.proto')

# https://github.com/AnyBlok/anyblok-book-examples/blob/III-06_polymorphism/Makefile
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

all: build_proto_modules

build_proto_modules: ${PROTOS}
	@echo "Build proto modules ..."
	@python setup.py build_proto_modules

sdist: ${SDIST_PACKAGE}

${SDIST_PACKAGE}: ${SOURCES}
	@echo "Building python project..."
	@python setup.py sdist

pypi-register:
	python setup.py register -r ${PYPI_REGISTER}
	
pypi-upload: ${SDIST_PACKAGE}
	twine upload \
		--repository ${PYPI_SERVER_FOR_UPLOAD} \
		--config-file ${PYPI_CONFIG_FILE} \
		dist/*

pip-install:
	@pip install \
		-r requirements_dev.txt \
		--trusted-host $(PYPI_SERVER_HOST) \
		--extra-index-url $(PYPI_SERVER) \
		--upgrade

pytest:
	pytest ${PYTEST_OPTIONS}

tox:
	# http://ahmetdal.org/jenkins-tox-shebang-problem/
	tox --workdir ${TOX_DIR}

clean: clean-proto clean-build clean-pyc ## remove all build, coverage and Python artifacts

clean-proto: ## remove Proto modules builds
	find src/pyconfr_2019/grpc_nlp/protos -name '*_pb2*.py*' -exec rm -fr {} +

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
