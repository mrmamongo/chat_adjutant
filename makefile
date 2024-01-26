flake:
	poetry run flake8 --per-file-ignores="__init__.py:F401" --ignore E203,E501,W503,PIE803,B008 main.py src

format:
	@echo "Форматирование"
	poetry run isort --profile black .
	poetry run black .