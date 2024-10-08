# -*- coding: utf-8 -*-
"""OpenCTI Malpedia client module."""
import json
import time
from typing import Any
from urllib.parse import urljoin

import requests
from pycti import OpenCTIConnectorHelper

from .constants import URLS_MAPPING


class MalpediaClient:
    """Malpedia client."""

    def __init__(self, helper: OpenCTIConnectorHelper, api_key: str) -> None:
        """Initialize Malpedia api client."""
        self.helper = helper
        self.api_key = api_key
        self.api_url = URLS_MAPPING["default_api_url"]

        if self.api_key == "" or self.api_key is None:
            self.unauthenticated = True
        else:
            self.unauthenticated = False
            if not self.token_check():
                raise ValueError(
                    "The API request failed because the token is invalid. "
                    "Please enter a valid auth_key or "
                    "run the connector in unauthenticated mode (no value)."
                )

    def api_response(self, url: str, retry_delay: int, auth: bool):
        if not auth:
            response = requests.get(url, timeout=30)
        else:
            prepared_headers = {"Authorization": "apitoken " + self.api_key}
            response = requests.get(url, headers=prepared_headers, timeout=30)

        if (
            response.status_code == 403
            and response.text == '{"detail": "Invalid token."}'
        ):
            self.helper.connector_logger.error(
                "[ERROR-API] The API request failed because the token is invalid.",
                {
                    "status_code": response.status_code,
                    "reason": response.reason,
                    "error": response.text,
                },
            )
            self.helper.metric.inc("client_error_count")
            return response.json()

        elif response.status_code == 404 and response.reason == "Not Found":
            detail = json.loads(response.text).get("detail", None)
            self.helper.connector_logger.info(
                "[API] The API request failed because the URL name does not exist for the identified actor :",
                {
                    "status_code": response.status_code,
                    "reason": response.reason,
                    "url": url,
                    "detail": detail,
                },
            )
            self.helper.metric.inc("client_error_count")
            return response.json()
        elif response.status_code == 429:
            available_in = json.loads(response.text).get("available_in", "0 seconds")
            delay, unit = available_in.split()

            self.helper.connector_logger.info(
                "[API] You have exceeded the speed or frequency limit allowed by the server, "
                "your request will automatically retry in seconds. "
                "If the value of available_in is greater than the value of retry_delay, "
                "we use the latter as the delay time.",
                {
                    "status_code": response.status_code,
                    "reason": response.reason,
                    "retry_delay_in_seconds": retry_delay,
                    "available_in": available_in,
                },
            )
            if retry_delay < int(delay):
                time.sleep(int(delay))
            else:
                time.sleep(retry_delay)
            return None
        elif response.status_code == 200:
            return response.json()
        else:
            self.helper.metric.inc("client_error_count")
            response.raise_for_status()
            return None

    def query(self, url_path: str) -> Any:
        url = urljoin(URLS_MAPPING["default_api_url"], url_path)
        try:

            max_retries = 3
            retry_delay = 65  # in second

            for _ in range(max_retries):
                if self.unauthenticated:
                    data = self.api_response(url, retry_delay, False)
                    if data is None:
                        continue
                    return data
                else:
                    data = self.api_response(url, retry_delay, True)
                    if data is None:
                        continue
                    return data

        except requests.exceptions.RequestException as e:
            self.helper.connector_logger.error(
                "[ERROR-API] Error in Malpedia query:", {"error": str(e)}
            )
            self.helper.metric.inc("client_error_count")
            return None
        except Exception as err:
            self.helper.connector_logger.error(
                "[ERROR-API] Some error occurred during a query with API",
                {"error": str(err)},
            )
            return None

    def token_check(self) -> bool:
        response_json = self.query("check/apikey")
        if response_json and "Valid token" in response_json["detail"]:
            return True
        else:
            return False

    def current_version(self) -> int:
        response_json = self.query("get/version")
        return int(response_json["version"])
