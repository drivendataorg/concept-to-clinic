Local development with Docker
=============================

Docker Compose is the only officially supported development configuration. We're doing this to stay focused on the project goals rather than triage lots of "not working on my machine" issues. If you wish to use virtualenvs instead, please ensure that you run all of the tests with Docker Compose before opening any Pull Requests.


The steps below will get you up and running with a local development environment.

**Note:** All of these commands assume you are in the root of your generated project.


## Prerequisites

### Install Docker

You'll need a recent version of Docker. If you don't already have it installed, follow the instructions for your OS:

- On Mac OS X, you'll need [`Docker for Mac`](https://docs.docker.com/engine/installation/mac/)
- On Windows, you'll need [`Docker for Windows`](https://docs.docker.com/engine/installation/windows/)  for 64bit Windows 10 Pro, Enterprise and Education or [`Docker Toolbox`](https://docs.docker.com/toolbox/overview/) for other versions
- On Linux, you'll need [`docker-engine`](https://docs.docker.com/engine/installation/)

Docker for Mac and Windows include Docker Compose, so most Mac and Windows users do not need to install it separately. For Linux users, follow the instructions for Linux installation in the [Docker documentation](https://docs.docker.com/compose/install/)


## Build the Stack

This can take a while, especially the first time you run this particular command
on your development system:

    $ docker-compose -f local.yml build


## Boot the System

This brings up the `interface app` (running Django), `prediction app` (running Flask), and PostgreSQL.

The first time it is run it might take a while to get started, but subsequent
runs will occur more quickly.

Open a terminal at the project root and run the following for local development:

    $ docker-compose -f local.yml up

You can also set the environment variable `COMPOSE_FILE` pointing to `local.yml` like this:

    $ export COMPOSE_FILE=local.yml

And then run:

    $ docker-compose up

You should now be able to open a browser and interact with the services:
 
- `interface` frontend at http://localhost:8080
- `interface` API at http://localhost:8000/api/
- `prediction` service at http://localhost:8001


## Code changes

Because `local.yml` has the volume mappings `./interface/:/app` and `./prediction/:/app` (the project dirs containing all of the code into the container's source code directory), changes made to files during development should be reflected in the running `interface` or `prediction` container as soon as the dev server process restarts.

## Running the tests

The `tests/test_docker.sh` shows you how to run the tests for both the prediciton and interface applications.

For example, if you are actively developing the prediction app, you could run the following to execute the tests:

    $ docker-compose -f local.yml run prediction pytest

## Other notes

### Pre-commit hooks
Git pre-commit hooks are useful tools that run commands before you commit. To enable easier maintainance of style guide and running tests, we implement pre-commit git hook commands that will run every time before you create a commit.

To set it up on your local development repository:

    $ cd concept-to-clinic

Copy the `.githook-pre-commit` file into the `.git/hooks/` folder as `pre-commit` with `-f` flag so that you overwrite any existing `pre-commit` file:

    $ cp -f .githook-pre-commit .git/hooks/pre-commit

Install `flake8` locally for the styling scripts:

    $ pip install flake8 pep8

You are set! The next time you want to commit, styling and testing pre-commit commands will be executed first and if they fail, your commit will not be committed.

If you want to by-pass the pre-commit check, use `--no-verify` flag in your commit:

    $ git commit --no-verify -m "Ignore pre-commit rules"

To check if the created pre-commit hook is working without having to do a commit, you can run from the root of the project:

    $ .git/hooks/pre-commit

### Detached Mode

If you want to run the stack in detached mode (in the background without console output), use the `-d` argument:

    $ docker-compose -f local.yml up -d

