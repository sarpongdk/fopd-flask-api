# Fopd Web Service

This RESTful backend web service is developed to abstract nuances and nitty-gritty details of working with a raspberry-pi controlled plant growing environments (a.k.a. Food Computer). A separate client is being developed independently to use provide a user friendly UI for using the web service

### Usage

#### Linux/Unix OS

<!-- A `.env` should be created in the following directory beforehand `./fopd`. If not, I have a script called `initialize.py` to automate the creation of the dotenv file in that directory. To run that script, execute:

```
python3 initialize.py
``` -->

Create a virtual environment with:

```
python3 -m venv _dir_name_here_
```

Upon creating the virtual environment, navigate to it via the command:

```
cd _dir_name_here_
```

Install the necessary dependencies for the project to run after setting up a virtual environment. Run:

```
make python-packages

# or

python3 -m pip install -r requirements.txt
```

to install the dependencies.

Initialize and create the db with the following command:

```
make create-db

# or

make db-init
make db-migrate
make db-upgrade

# or

python3 manage.py db init
python3 manage.py db migrate
python3 manage.py db upgrade

```

To run the project:

```
make run

# or

python3 manage.py run
```

The `Makefile` provided here contains all the necessary commands to recreate and run the application

```
MANAGE=manage.py

.PHONY: clean python-packages install db run all

help:
	@echo "Navigate into the root directory and set up a virtual environment"
	@echo "To create the virtual env execute `python3 -m  venv {dirname}`
	@echo ""
	@echo "Please use \`make <target>' where <target> is one of"
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
```
