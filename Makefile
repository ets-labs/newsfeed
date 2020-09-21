clean:
	find src -type f -name "*.py[co]" -delete
	find src -type d -name "__pycache__" -delete

lint: clean
	flake8 src/newsfeed tests
	mypy -p newsfeed

test: clean
	py.test tests/unit --cov=src/

integration-test:
	python scripts/integration_check.py
	echo "Tests passed"

