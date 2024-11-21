from datetime import datetime

def convert_html_date_time_to_time(date_time_str):
    return datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M') #'2015-01-02T00:00'

def check_is_float_and_convert(str):
    try:
        float(str)
        return float(str)
    
    except ValueError:
        return False
