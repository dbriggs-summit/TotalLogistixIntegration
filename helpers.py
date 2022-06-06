from carrier_codes import carrier_codes


def clean_amount(amount):
    if amount == 'null':
        return 0.00
    # keep default
    return amount

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