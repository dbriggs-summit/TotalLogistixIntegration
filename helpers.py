from carrier_codes import carrier_codes
from datetime import datetime

def clean_amount(amount):
    if amount == 'null':
        return 0.00
    # keep default
    return amount

def clean_delayed_reason(delayed_reason):
    if delayed_reason == 'null':
        return ''
    # keep default
    return delayed_reason

def format_tracking(carrier_code, tracking):
    # transform central transport tracking
    # to include hypens ex. 555-1234567-1
    if carrier_code in ['CTII','CETR'] and len(tracking.strip()) == 11:
        tracking = tracking
        dashed_tracking = tracking[:3] + '-' + tracking[3:]
        dashed_tracking = dashed_tracking[0:-1] + '-' + dashed_tracking[-1]
        return dashed_tracking

    # keep default
    return tracking

def get_carrier_name(carrier_code):
    shipvia = ""
    try:
        shipvia = carrier_codes[carrier_code]
    except KeyError:
        shipvia = carrier_code

    return shipvia

def valid_date_format(input_date):
    date_format = "%Y-%m-%d"
    try:
        return bool(datetime.strptime(input_date, date_format))
    except ValueError:
        return False