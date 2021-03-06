# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import logging
import sys

from flask import Flask, render_template

from seniority_visualizer_app import commands, public, seniority, user
from seniority_visualizer_app.extensions import (
    bcrypt,
    cache,
    csrf_protect,
    db,
    debug_toolbar,
    login_manager,
    mail,
    migrate,
    webpack,
)


def create_app(config_object="seniority_visualizer_app.settings"):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    configure_logger(app)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    register_request_hooks(app)
    configure_jinja(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    cache.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    webpack.init_app(app)
    mail.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    app.register_blueprint(seniority.views.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template("{0}.html".format(error_code)), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db, "User": user.models.User, "Role": user.models.Role}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.add)
    app.cli.add_command(commands.create_user)


def configure_logger(app):
    """Configure loggers."""
    app_logger: logging.Logger = app.logger

    loggers = [
        app_logger,
    ]

    handler = logging.StreamHandler(sys.stdout)

    level = "DEBUG" if app.config.get("FLASK_DEBUG") else "INFO"

    handler.setLevel(getattr(logging, level))

    for logger in loggers:
        del logger.handlers[:]
        logger.addHandler(handler)
        logger.setLevel(level)


def register_request_hooks(app):
    @app.before_first_request
    def populate_db():
        from seniority_visualizer_app.user.role import Role

        app.logger.info("updating role permissions")
        Role.insert_roles()


def configure_jinja(app: Flask):
    """Configure Jinja templating engine and register filters"""
    from .jinja_filters import format_datetime

    app.jinja_env.filters["datetime"] = format_datetime
