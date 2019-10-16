clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

test: clean
	py.test

integration-test:
	python scripts/integration_check.py
	echo "Tests passed"

lint: clean
	flake8 newsfeed tests
