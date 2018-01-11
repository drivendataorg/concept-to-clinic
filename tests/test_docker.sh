#!/bin/sh
# adapted from pydanny/cookiecutter-django
#
# this is a very simple script that tests the docker configuration
# it is meant to be run from the root directory of the repository, eg:
# sh tests/test_docker.sh
set -ex

# run the model service's tests
# Coverage should ignore pip packets, files including tests and pytest
docker-compose -f local.yml run prediction coverage run --branch --omit=/**/dist-packages/*,src/tests/*,/usr/local/bin/pytest /usr/local/bin/pytest -rsx
docker-compose -f local.yml run prediction coverage report

# run the backend API tests
# Coverage should ignore pip packets, files including migrations and tests
docker-compose -f local.yml run interface coverage run --branch --omit=/**/dist-packages/*,**/migrations/*.py,**/test*.py manage.py test
docker-compose -f local.yml run interface coverage report

# return non-zero status code if there are migrations that have not been created
docker-compose -f local.yml run interface python manage.py makemigrations --dry-run --check || { echo "ERROR: there were changes in the models, but migration listed above have not been created and are not saved in version control"; exit 1; }

# Run unit and e2e test
#docker-compose -f local.yml run vue_unit_test

#docker-compose -f local.yml run vue_e2e_test
