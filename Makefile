test:
	pytest tests --import-mode=prepend --junitxml=report.xml
coverage:
	pytest --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=ifcclient tests
publish:
	pip3 install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist .egg ifcclient.egg-info
build:
	python setup.py sdist bdist_wheel

clean:
	rm -fr build dist .egg ifcclient.egg-info