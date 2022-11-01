import os
import tempfile

import pytest
from dotenv import load_dotenv

from web import create_app

load_dotenv()


@pytest.fixture()
def web_address():
    url = f"{os.getenv('COUSCOUS_WEB_PROTOCOL')}://{os.getenv('COUSCOUS_WEB_HOST')}"
    port = os.getenv('COUSCOUS_WEB_PORT')
    if port and int(port) > 1024:
        url += f":{port}"
    return url


@pytest.fixture()
def api_address():
    url = f"{os.getenv('COUSCOUS_API_PROTOCOL')}://{os.getenv('COUSCOUS_API_HOST')}"
    port = os.getenv('COUSCOUS_API_PORT')
    if port and int(port) > 1024:
        url += f":{port}"
    return url


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
    })

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()