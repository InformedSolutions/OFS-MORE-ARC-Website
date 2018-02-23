# Include Makefile settings
-include .makerc

# Detect OS
ifeq ($(OS),Windows_NT)
	WIN := 1
endif

# Define python binary depedant on OS
ifdef WIN
	PYTHON_BIN = python
	PIP_BIN = python
else
	PYTHON_BIN = .venv/bin/python3
	PIP_BIN = .venv/bin/pip3
endif

# run server
run:
	$(PYTHON_BIN) manage.py runserver $(PROJECT_IP):$(PROJECT_PORT)  --settings=$(PROJECT_SETTINGS)

# run tests
test:
	$(PYTHON_BIN) manage.py test --settings=$(PROJECT_SETTINGS)

# install depedencies (and virtualenv for linux)
install:
ifndef WIN
	-virtualenv -p python3 .venv
endif
	$(PIP_BIN) install -r requirements.txt

# handle django migrations
migrate:
	$(PYTHON_BIN) manage.py makemigrations --settings=$(PROJECT_SETTINGS)
	$(PYTHON_BIN) manage.py migrate --settings=$(PROJECT_SETTINGS)

# handle statics
static:
	$(PYTHON_BIN) manage.py collectstatic --settings=$(PROJECT_SETTINGS)

