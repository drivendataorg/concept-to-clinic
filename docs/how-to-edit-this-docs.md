How to Edit This Document
=========================

This documentation is a [sphinx](http://www.sphinx-doc.org) project. From this
section, you will get set on how to build, install, edit and view documentation
locally on your development environment.

The documentation files are located in the `docs` folder.

For this documentation, source filenames that are allowed are [Markdown](https://daringfireball.net/projects/markdown/) (ending with `.md`)
and [reStructuredText](http://docutils.sourceforge.net/rst.html) (ending with
`.rst`) files.

How to Install & Build Locally
------------------------------

Since [Docker](https://www.docker.com/) is the officially supported
development configuration, when you start the [local development with docker](https://concept-to-clinic.readthedocs.io/en/latest/developing-locally-docker.html),
the `documentation service` is also started.

Navigate to [http://localhost:8002/](http://localhost:8002/) to view the docs,
once your local server is up.

## Code changes

Because `local.yml` has the volume mappings `./:/app` and
`./docs/_build/html:/app/docs/_build/html`, changes made to files
during development should be reflected in the running `documentation` container
as soon as the dev server process restarts. The `compile_docs` container has a
`restart: always` configuration to allow the docs application to automatically
compile the markdown and reStructuredText files in the project into `html` and
then, sync these files.

So when you do a change in the docs, instead of restarting all services, or
if you're running them in daemon mode, when you reload the documentation page,
your changes will reflect.

## Running the tests

The `tests/test_docker.sh` shows you how to run the tests for the documentation
application.

    $ docker-compose -f local.yml run documentation make -C /app/docs doctest

How to Update Table of Contents
-------------------------------

The table of contents can be updated using `markdown` or `reStructuredText`
files.

To add a new table of contents section to the current one, the file(s) with the
section's content have to be linked using sphinx from the entry-point file of
the project i.e. `index.rst`.

**Example:**

In the current `index.rst`, it includes a root `toctree` directive, under which
we can add content files or create new `toctree` sections for the table of
contents.

```markdown
...
.. toctree::
   :maxdepth: 4 #indicate maximum depth of your tree
   :caption: Descriptive caption

   top-level-file-1
   top-level-file-2
   ...
...
```
Here `top-level-file-1` and `top-level-file-2` can be markdown or reST files
corresponding to `top-level-file-1.md` or `top-level-file-2.rst` in the local
path.

This will render like this on the table of contents:

  ...
  * [Descriptive caption](#)
    * [Top level file 1](#)
    * [Top level file 2](#)

  ...


You can read more about toctree
[here](http://www.sphinx-doc.org/en/stable/markup/toctree.html)

Useful Links
------------

When writing the documentation, **markdown** is the easiest to use and adapt
to. You can have a look at
[this cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)
to help you in writing the markdown files.

If you prefer using **reST** markup, you can have a look at their
[documentation](http://docutils.sourceforge.net/rst.html) and also the official
[sphinx documentation](http://www.sphinx-doc.org) which details the various
directives, their purpose and how to use them.

This [example PyPi project](https://pythonhosted.org/an_example_pypi_project/sphinx.html)
also details some of the commands available via sphinx.
