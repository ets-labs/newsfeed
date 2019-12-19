clean:
	find src -type f -name "*.py[co]" -delete
	find src -type d -name "__pycache__" -delete

test: clean
	py.test --cov=src/

integration-test:
	python scripts/integration_check.py
	echo "Tests passed"

lint: clean
	flake8 src/newsfeed tests
	mypy -p newsfeed
