help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-test clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

test:
	python setup.py test --pytest-args="--cov=./djmoney tests"

coverage:
	coverage run --source djmoney setup.py test
	coverage report -m
	coverage html

install: clean
	python setup.py install

release: dist  ## Generate and upload release to PyPi
	twine upload -s dist/*

dist: clean  ## Generate source dist and wheels
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist
