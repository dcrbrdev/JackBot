import json

import requests

from utils.exceptions import DcrDataAPIError


DCRDATA_API_URL = "https://dcrdata.decred.org/api"


def request_dcr_data(endpoint):
    dcrdata_response = requests.get(f"{DCRDATA_API_URL}/{endpoint}")
    if dcrdata_response.status_code != 200:
        raise DcrDataAPIError(dcrdata_response.content)

    return json.loads(dcrdata_response.content)
