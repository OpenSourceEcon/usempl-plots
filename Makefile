format:
	black . -l 79
	linecheck . --fix

test:
	pytest -m 'not local' --cov=./ --cov-report=xml --maxfail=0

pip-package:
	pip install wheel
	pip install setuptools
	python setup.py sdist bdist_wheel
