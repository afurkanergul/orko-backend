setup:
	pip install -r requirements.txt
	pre-commit install

run:
	uvicorn main:app --reload

test:
	pytest -v

format:
	black . && isort .

lint:
	flake8 .
