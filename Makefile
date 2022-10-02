publish:
	pip3 install 'twine>=1.5.0'
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist .egg ifcclient.egg-info
build:
	python setup.py sdist bdist_wheel

clean:
	rm -fr build dist .egg ifcclient.egg-info