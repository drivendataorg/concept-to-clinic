#!/bin/sh
# adapted from pydanny/cookiecutter-django
#
# this is a very simple script that tests the docker configuration
# it is meant to be run from the root directory of the repository, eg:
# sh tests/test_docker.sh
set -ex

# run the model service's tests
docker-compose -f local.yml run prediction pytest -rs

# run the backend API tests
docker-compose -f local.yml run interface python manage.py test

# run the frontend tests
# docker-compose -f local.yml run vue npm run e2e

# run the documentation's tests
# docker-compose -f local.yml run documentation make -C /app/docs doctest

# return non-zero status code if there are migrations that have not been created
docker-compose -f local.yml run interface python manage.py makemigrations --dry-run --check || { echo "ERROR: there were changes in the models, but migration listed above have not been created and are not saved in version control"; exit 1; }
