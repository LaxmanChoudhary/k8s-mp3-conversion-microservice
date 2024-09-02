import os
import datetime
import jwt
from flask import Flask, request
from flask_mysqldb import MySQL
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

server = Flask(__name__)
mysql = MySQL(server)

server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    cur = mysql.connection.cursor()
    res = cur.execute("SELECT email, password FROM user WHERE email=%s", (auth.username,))

    if res > 0:
        # at least one row returned
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return create_jwt(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return "invalid credentials", 401


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers['Authorization']
    if not encoded_jwt:
        return "missing credentials", 401

    encoded_jwt = encoded_jwt.split(" ")[1]
    server.logger.info("encoded jwt: %s", encoded_jwt)
    server.logger.info("secret: %s", os.environ.get("JWT_SECRET"))
    try:
        decoded = jwt.decode(encoded_jwt, os.environ.get("JWT_SECRET"), algorithms="HS256")
    except Exception as ex:
        server.logger.error(ex)
        return "not authorized", 401

    return decoded, 200


def create_jwt(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "expiration": (datetime.datetime.utcnow() + datetime.timedelta(days=1)).timestamp(),
            "iat": datetime.datetime.utcnow().timestamp(),
            "admin": authz
        },
        secret,
        algorithm="HS256",
    )


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)

