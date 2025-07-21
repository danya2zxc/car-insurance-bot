run:
	python -m app.main

start:
	watchmedo auto-restart --patterns="*.py;*.env" --recursive -- python -m app.main
