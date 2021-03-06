===============================
Seniority Visualizer App
===============================

A seniority visualizer for airline pilots


What's This?
------------
Some time ago, my company had a pretty simplistic webapp that would give you a good idea about the seniority
a pilot could expect to achieve by their retirement date. This webapp allows for a greater introspection into
the career trajectory of a company's pilot group. It isn't currently meant to be deployable for anyone other
than myself, with the data I point it at. However, a fork will be created when I make a stable app that will
allow for anyone to deploy with simply a configuration file and a .csv file with the current seniority data
of their company.


Where all da README at?
------------------------
It's coming, chill.


Quickstart
----------

Run the following commands to bootstrap your environment ::

    git clone https://github.com/AirbusDriver/seniority_visualizer_app
    cd seniority_visualizer_app
    pipenv install --dev
    cp .env.example .env
    npm install
    npm start  # run the webpack dev server and flask server using concurrently

You will see a pretty welcome screen.

Once you have installed your DBMS, run the following to create your app's
database tables and perform the initial migration ::

    flask db init
    flask db migrate
    flask db upgrade
    npm start


Deployment
----------

To deploy::

    export FLASK_ENV=production
    export FLASK_DEBUG=0
    export DATABASE_URL="<YOUR DATABASE URL>"
    npm run build   # build assets with webpack
    flask run       # start the flask server

In your production environment, make sure the ``FLASK_DEBUG`` environment
variable is unset or is set to ``0``.


Shell
-----

To open the interactive shell, run ::

    flask shell

By default, you will have access to the flask ``app``.


Running Tests/Linter
--------------------

To run all tests, run ::

    flask test

To run the linter, run ::

    flask lint

The ``lint`` command will attempt to fix any linting/style errors in the code. If you only want to know if the code will pass CI and do not wish for the linter to make changes, add the ``--check`` argument.

Migrations
----------

Whenever a database migration needs to be made. Run the following commands ::

    flask db migrate

This will generate a new migration script. Then run ::

    flask db upgrade

To apply the migration.

For a full migration command reference, run ``flask db --help``.


Docker
------

This app can be run completely using ``Docker`` and ``docker-compose``. Before starting, make sure to create a new copy of ``.env.example`` called ``.env``. You will need to start the development version of the app at least once before running other Docker commands, as starting the dev app bootstraps a necessary file, ``webpack/manifest.json``.

There are three main services:

To run the development version of the app ::

    docker-compose up flask-dev

To run the production version of the app ::

    docker-compose up flask-prod

The list of ``environment:`` variables in the ``docker-compose.yml`` file takes precedence over any variables specified in ``.env``.

To run any commands using the ``Flask CLI`` ::

    docker-compose run --rm manage <<COMMAND>>

Therefore, to initialize a database you would run ::

    docker-compose run --rm manage db init

A docker volume ``node-modules`` is created to store NPM packages and is reused across the dev and prod versions of the application. For the purposes of DB testing with ``sqlite``, the file ``dev.db`` is mounted to all containers. This volume mount should be removed from ``docker-compose.yml`` if a production DB server is used.


Asset Management
----------------

Files placed inside the ``assets`` directory and its subdirectories
(excluding ``js`` and ``css``) will be copied by webpack's
``file-loader`` into the ``static/build`` directory, with hashes of
their contents appended to their names.  For instance, if you have the
file ``assets/img/favicon.ico``, this will get copied into something
like
``static/build/img/favicon.fec40b1d14528bf9179da3b6b78079ad.ico``.
You can then put this line into your header::

    <link rel="shortcut icon" href="{{asset_url_for('img/favicon.ico') }}">

to refer to it inside your HTML page.  If all of your static files are
managed this way, then their filenames will change whenever their
contents do, and you can ask Flask to tell web browsers that they
should cache all your assets forever by including the following line
in your ``settings.py``::

    SEND_FILE_MAX_AGE_DEFAULT = 31556926  # one year



Configuration
-------------

In its current deployment implementation, a private branch is used that contains
the datasource that is loaded into memory. That should be set in the ``settings.py`` file.
The ``tests/settings.py`` module has an example of this. This wil change in the future
as a repository layer is implemented.


Updating the Datasource
-----------------------

The new datasource should be added to the local branch by conforming the format
to the current field map. This is important because all of the data functionality
will be limited to using the ``STANDARD_FIELDS`` object.

::

    fields = {
            "seniority_number": STANDARD_FIELDS.SENIORITY_NUMBER,
            "cmid": STANDARD_FIELDS.EMPLOYEE_ID,
            "base": STANDARD_FIELDS.BASE,
            "seat": STANDARD_FIELDS.SEAT,
            "retire_date": STANDARD_FIELDS.RETIRE_DATE,
            "fleet": STANDARD_FIELDS.FLEET,
        }
