#!/usr/bin/python
# coding: utf8

import json
import requests
from urllib.parse import urlencode
from var_dump import var_dump


class Api:
    user = None

    def __init__(self):
        self.url = "https://api.eurobilltracker.com"

    def get(self, method: str, version: str, params={}):
        url = f"{self.url}/?m={method}&v={version}"

        if self.user:
            url = f"{url}&PHPSESSID={self.user['sessionid']}"

        if params:
            url_encoded_string = urlencode(params, doseq=True)
            url = f"{url}&{url_encoded_string}"

        res = requests.get(url)

        if res.status_code != 200:
            raise Exception(f"Error")

        try:
            # Attempt to decode JSON data
            data = res.json()
        except json.JSONDecodeError as e:
            # if bytes are encode
            json_string = res._content.decode("utf-8-sig")
            data = json.loads(json_string)

        return data

    def login(self, email: str, password: str):

        res = requests.post(
            self.url + "?m=login&v=2", {"my_email": email, "my_password": password}
        )

        if res.status_code == 200:
            self.user = res.json()
        else:
            raise Exception(f"Error")

    def logout(self):
        return self.get("logout", "1")

    def get_cities(self):
        return self.get("mycities", "1")

    def get_zipcodes(self, city: str, country: str, comment: str = ""):
        return self.get(
            "myzipcodes", "1", {"city": city, "country": country, "comment": comment}
        )

    def insert_note(
        self,
        country: str,
        city: str,
        zip_code: str,
        value: int,
        short_code: str,
        serial_number: str,
        comment: str = "",
    ):
        return self.get(
            "insertbills",
            "1",
            {
                "city": city,
                "zip": zip_code,
                "country": country,
                "denomination0": value,
                "shortcode0": short_code,
                "serial0": serial_number,
                "comment0": comment,
            },
        )

    def search(self, term: str, type: int = 0, limit: int = 0, cursor: int = 0):
        """
        :param str term: the search term; minimum length 3 characters
        :param str type: 1 - only users; 2 - only cities; 3 - only countries
        :param str limit: The desired maximum number of results per page. By default all results will be returned
        :param str cursor: The cursor/requested page starting from 0; e.g. if c=1 and pp=50 the results 51-100 will be returned
        """

        params = {"find": term}

        if type:
            params["what"] = type

        if limit:
            params["pp"] = limit

        if cursor:
            params["c"] = cursor

        return self.get("search", "1", params)
