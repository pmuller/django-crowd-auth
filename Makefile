# Project configuration
PACKAGE = django_crowd_auth

# Call these functions before/after each target to maintain a coherent
# display
START_TARGET = @printf -- "\033[38;5;33m%s\033[0m\n" "$(1)"
END_TARGET = @printf "\033[38;5;46mOK\033[0m\n\n"

# Parameter expansion
PYTEST_OPTS ?=

.PHONY: help check_code_style check_doc_style check_pylint check_xenon \
        check_lint check_test check distclean clean doc dist

help: ## Display list of targets and their documentation
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk \
		'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

doc: ## Generate documentation
	$(call START_TARGET,Generating documentation)
	@make -C doc html
	$(call END_TARGET)

check_code_style: ## Apply code style checks
	$(call START_TARGET,Checking code style)
	@pycodestyle $(PACKAGE)
	$(call END_TARGET)


check_doc_style: ## Apply doc style checks
	$(call START_TARGET,Checking doc style)
	@pydocstyle $(PACKAGE)
	@make -s -C doc dummy > /dev/null
	$(call END_TARGET)


check_pylint: ## Apply pylint checks (code quality)
	$(call START_TARGET,Checking pylint)
	@pylint --reports=no --jobs=2 $(PACKAGE)
	$(call END_TARGET)


check_xenon: ## Apply xenon checks (code complexity)
	$(call START_TARGET,Checking xenon)
	@xenon $(PACKAGE) --no-assert
	$(call END_TARGET)


check_lint: check_code_style check_doc_style check_pylint check_xenon ## Call check_code_style, check_doc_style, check_pylint, check_xenon


check_test: ## Apply py.test
	$(call START_TARGET,Checking tests)
	@py.test $(PYTEST_OPTS)


check: check_lint check_test ## Call check_lint, check_test


dist: ## Create a source distribution
	$(call START_TARGET,Creating distribution)
	@python setup.py --quiet sdist
	$(call END_TARGET)


distclean: clean ## Remove source distributions
	$(call START_TARGET,Distribution cleaning)
	@rm -rf *.egg-info
	@rm -rf dist
	$(call END_TARGET)


clean: ## Cleanup development files
	$(call START_TARGET,Cleaning)
	@make -C doc clean
	@find . -type f -name '*.pyc' -delete
	@rm -rf dist/* .cache .eggs
	@rm -rf htmlcov .coverage
	$(call END_TARGET)
