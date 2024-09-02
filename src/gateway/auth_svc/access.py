import os, requests

import flask


def login(request: flask.Request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)

    basic_auth = (auth.username, auth.password)
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
        auth=basic_auth
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
