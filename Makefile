MANAGE=manage.py

.PHONY: clean python-packages install db run all

help:
	@echo "Navigate into the root directory and set up a virtual environment"
	@echo "To create the virtual env execute python3 -m  venv {dirname}"
	@echo "Install the necessary dependencies for the project with the command make python-packages"
	@echo ""
	@echo "Please use \`make <target>\' where <target> is one of"
	@echo "  clean      to clean project directory"
	@echo "  install    to install application dependencies with pip"
	@echo "  db-init    to initialize application database"
	@echo "  db         to initialize and upgrade application database"
	@echo "  run        to run project"

clean:
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type f -name '*.pyc' -delete

python-packages:
	pip install -r requirements.txt

install:  python-packages

run:
	python $(MANAGE) run

db-init:
	python $(MANAGE) db init

db-upgrade:
	python $(MANAGE) db upgrade

db-migrate:
	python $(MANAGE) db migrate

db-downgrade:
	python $(MANAGE) db downgrade

create-db: db-init db-migrate db-upgrade 

all: clean install db run