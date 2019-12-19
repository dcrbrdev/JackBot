import json

import requests

from bot.exceptions import DcrDataAPIError


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def convert_dcr(dcr_amount: float, target_currency: str):
    dcrdata_response = requests.get(f"https://dcrdata.decred.org/api/exchanges?"
                                    f"code={target_currency}")
    if dcrdata_response.status_code != 200:
        raise DcrDataAPIError(dcrdata_response.content)

    dcr_to_usd_value = json.loads(dcrdata_response.content)
    dcr_to_usd_value = dcr_to_usd_value.get("price")

    if target_currency == 'USD':
        return dcr_amount*dcr_to_usd_value
