from datetime import datetime

def datetime_to_int_seconds(dt_obj):
    """Converts a datetime object to integer seconds"""
    epoch_start = datetime(1970, 1, 1)
    if type(dt_obj) is not datetime:
        raise ('{} must be type, datetime but is {}'.format(dt_obj,type(dt_obj)))

    return int((dt_obj - epoch_start).total_seconds())
