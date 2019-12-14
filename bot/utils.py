import json

import requests

from bot.exceptions import DcrDataAPIError, ExchangeAPIError


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
    dcrdata_response = requests.get("https://dcrdata.decred.org/api/exchanges")
    if dcrdata_response.status_code != 200:
        raise DcrDataAPIError(dcrdata_response.content)

    dcr_to_usd_value = json.loads(dcrdata_response.content)
    dcr_to_usd_value = dcr_to_usd_value.get("price")

    if target_currency == 'USD':
        return dcr_amount*dcr_to_usd_value

    exchangerate_response = requests.get(f"https://api.exchangeratesapi.io/latest?base=USD&symbols={target_currency}")
    if exchangerate_response.status_code != 200:
        raise ExchangeAPIError(f"Currency {target_currency} is not valid!\n"
                               f"Choose one from https://api.exchangeratesapi.io/latest")

    usd_to_target_value = json.loads(exchangerate_response.content)
    usd_to_target_value = usd_to_target_value.get("rates").get(target_currency)

    return dcr_amount*dcr_to_usd_value*usd_to_target_value
