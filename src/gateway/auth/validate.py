import os, requests

import flask


def token(request: flask.Request):
    if "Authorization" not in request.headers:
        return None, ("missing credentials", 401)

    token_v = request.headers["Authorization"]

    if not token_v:
        return None, ("missing credentials", 401)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token_v}
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
