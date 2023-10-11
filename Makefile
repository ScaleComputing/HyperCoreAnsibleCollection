# Make sure we have ansible_collections/scale_computing/hypercore as a prefix. This is
# ugly as hack, but it works. I suggest all future developer to treat next few
# lines as an opportunity to learn a thing or two about GNU make ;)
collection := $(notdir $(realpath $(CURDIR)      ))
namespace  := $(notdir $(realpath $(CURDIR)/..   ))
toplevel   := $(notdir $(realpath $(CURDIR)/../..))

err_msg := Place collection at <WHATEVER>/ansible_collections/scale_computing/hypercore
ifeq (true,$(CI))
  $(info Running in CI setting, skipping directory checks.)
else ifneq (hypercore,$(collection))
  $(error $(err_msg))
else ifneq (scale_computing,$(namespace))
  $(error $(err_msg))
else ifneq (ansible_collections,$(toplevel))
  $(error $(err_msg))
endif

python_version := $(shell \
  python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' \
)

unit_test_targets := $(shell find tests/unit -name '*.py')
integration_test_targets := $(shell ls tests/integration/targets)


.PHONY: help
help:
	@echo Available targets:
	@fgrep "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort

# Developer convenience targets

.PHONY: format
format:  ## Format python code with black
	black -t py38 plugins tests/unit
	ansible-lint --write

.PHONY: clean
clean:  ## Remove all auto-generated files
	rm -rf tests/output

.PHONY: $(unit_test_targets)
$(unit_test_targets):
	ansible-test units --requirements --python $(python_version) $@

.PHONY: $(integration_test_targets)
$(integration_test_targets):
	ansible-test integration --requirements --python $(python_version) --diff $@

# Things also used in CI/CD

.PHONY: sanity
sanity:  ## Run sanity tests
	pip install -r sanity.requirements
	black -t py38 --check --diff --color plugins tests/unit
	ansible-lint
	flake8 --exclude tests/output/
	ansible-test sanity --docker

.PHONY: units
units:  ## Run unit tests
	-ansible-test coverage erase # On first run, there is nothing to erase.
	ansible-test units --docker --coverage
	ansible-test coverage html --requirements
	ansible-test coverage report --omit 'tests/*' --show-missing

.PHONY: integration
integration:  ## Run integration tests
	ansible-test integration --docker --diff

.PHONY: docs
docs:  ## Build collection documentation
	pip install -r docs.requirements
	pip install -r docs/requirements.txt
	cd docs && ANSIBLE_COLLECTIONS_PATH=${PWD}/../../.. ./build.sh

.PHONY: mypy
mypy: ## Run mypy hint checker
	pip install -r mypy.requirements
	mypy -p plugins
