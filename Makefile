clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

test: clean
	py.test

lint: clean
	flake8 newsfeed tests
