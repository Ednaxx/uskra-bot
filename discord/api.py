import logging
from requests import HTTPError
from util.constants import *
import requests


def request(path: str, auth_token: str, method: str = "GET", body: dict | None = None) -> requests.Response:
    logging.info(f" Requesting {method} {path}{' ' + str(body) if (body is not None) else ''}...")

    url = BASE_URL + path
    headers = {"Authorization": f"Bot {auth_token}"}

    try:
        response = requests.request(method, url, json=body, headers=headers)
        response.raise_for_status()
        logging.info(f" Response: {response.json()}")
        return response
    except HTTPError as e:
        logging.warning(" HTTP Error: " + str(e))
        return e.response


if __name__ == "__main__":
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    response = request("/gateway/bot")
    print(response)
