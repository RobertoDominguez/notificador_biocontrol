import requests
import json
import time

class ConnAPI:
    def __init__(
        self,
        base_url,
        token=None,
        headers=None,
        timeout=10
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.headers = headers or {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if token:
            self.headers["x-api-key"] = f"{token}"

    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.get(
            url,
            params=params,
            headers=self.headers,
            timeout=self.timeout
        )
        self._validate_response(response)
        return response.json()

    def post(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.post(
            url,
            json=data,
            headers=self.headers,
            timeout=self.timeout
        )
        self._validate_response(response)
        return response.json()

    def _validate_response(self, response):
        if response.status_code >= 400:
            raise Exception(
                f"API Error {response.status_code}: {response.text}"
            )