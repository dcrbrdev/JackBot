from utils.dcrdata import request_dcr_data


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
    endpoint = "exchanges"
    dcr_to_usd_value = request_dcr_data(endpoint)
    dcr_to_usd_value = dcr_to_usd_value.get("price")

    if target_currency == 'USD':
        return dcr_amount * dcr_to_usd_value
