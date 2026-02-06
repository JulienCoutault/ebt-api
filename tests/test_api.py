#!/usr/bin/python
# coding: utf8

import base64
import os

from dotenv import load_dotenv

from ebt import Api

load_dotenv()


def setup_api() -> Api:
    api = Api()

    api.login(os.getenv("LOGIN"), os.getenv("PASSWORD"))

    return api


if __name__ == "__main__":

    def test_login():
        setup_api()
