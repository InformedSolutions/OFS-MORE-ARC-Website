-include .makerc

run:
	$(PYTHON_CMD) manage.py runserver --settings=arc_service.settings.de
test:
	$(PYTHON_CMD) manage.py test --settings=arc_service.settings.dev
install:
	$(PIP_CMD) install -r requirements.txt
migrate:
	$(PYTHON_CMD) manage.py makemigrations --settings=arc_service.settings.dev
	$(PYTHON_CMD) manage.py migrate --settings=arc_service.settings.dev
