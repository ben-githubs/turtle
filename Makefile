test:
	pytest


lint:
	ruff check
	ruff format --check


fmt:
	ruff format