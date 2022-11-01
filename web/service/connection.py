import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import url_for
from werkzeug.utils import redirect

from web.config import API_ROUTES


def call_api(*, route, headers=None, post_data=None, next=None):
    error = None
    if post_data:
        headers = {"Content-Type": "application/json"}
        data = json.dumps(post_data).encode('utf-8')

    request = Request(
        API_ROUTES[route],
        headers=headers or {},
        data=post_data
    )
    try:
        with urlopen(request, timeout=5) as response:
            body = response.read()
    except HTTPError as exc:
        error = f"HTTP Error {exc.status} happens. Reason: {exc.reason}"
    except URLError as exc:
        error = f"Exception happens. Reason: {exc.reason}"
    except TimeoutError:
        error = f"Timed out request."
    else:
        if error:
            return error
        if next:
            return redirect(url_for(next), body)
        else:
            return json.loads(body)
