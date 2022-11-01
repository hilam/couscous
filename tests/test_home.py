from urllib.error import URLError
from urllib.request import urlopen

import pytest


def test_request_home_sem_servidor_retorna_URLError(web_address):
    with pytest.raises(URLError):
        response = urlopen(web_address)


def test_request_home_com_servidor_retorna_200(client):
    response = client.get('/')
    assert response.status_code == 200