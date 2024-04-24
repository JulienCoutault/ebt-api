#!/usr/bin/python
# coding: utf8

import base64
import os

from dotenv import load_dotenv

from ebt import Api

load_dotenv()


def decrypt(str):
    return base64.b64decode(str.encode("ascii")).decode("ascii")


def setup_api() -> Api:
    api = Api()

    # I don't want to see password in clear even in env file
    api.login(decrypt(os.getenv("LOGIN")), decrypt(os.getenv("PASSWORD")))

    return api


if __name__ == "__main__":

    def test_login():
        setup_api()
