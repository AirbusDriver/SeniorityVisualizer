import pytest
import logging


@pytest.fixture
def production_config(app):
    """Reconfigure logging for production"""
    from seniority_visualizer_app.app import configure_logger
    app.config["FLASK_DEBUG"] = 0
    app.config["FLASK_ENV"] = "production"
    app.config["TESTING"] = False

    configure_logger(app)

    yield app


def test_production_logger_level(production_config):
    """Test the logger is set to INFO in production"""
    logger = logging.getLogger()

    assert logger.level == logging.INFO
    assert production_config.logger.level == logging.INFO
