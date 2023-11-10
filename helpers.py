from carrier_codes import carrier_codes
from parcel_codes import parcel_codes
from datetime import datetime, timedelta

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

def get_parcel_carrier_name(parcel_code):
    shipvia = ""
    try:
        shipvia = parcel_codes[parcel_code]
    except KeyError:
        shipvia = parcel_code

    return shipvia

def valid_date_format(input_date):
    date_format = "%Y-%m-%d"
    try:
        return bool(datetime.strptime(input_date, date_format))
    except ValueError:
        return False

# Return 1 day after the given date, skipping weekends
def set_delivered_date(date_string):
    date_object = datetime.strptime(date_string, "%m/%d/%Y")

    # Loop until a non-weekend date is found
    while True:
        date_object += timedelta(days=1)
        if not is_weekend(date_object):
            break

    return date_object.strftime("%m/%d/%Y")

def is_weekend(date):
    return date.weekday() in [5, 6]  # 5 is Saturday, 6 is Sunday
