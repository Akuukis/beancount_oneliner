install:
	pip3 install -r requirements.txt

lint:
	black beancount_allocate/

test:
	pytest

clean:
	rm -rf build dist beancount_oneliner.egg-info/

build: clean
	python3 setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

.PHONY: init test
