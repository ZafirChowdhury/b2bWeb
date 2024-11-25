from datetime import datetime

import requests

def convert_html_date_time_to_python_datetime(date_time_str):
    return datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M') #'2015-01-02T00:00'


def check_is_float_and_convert(str):
    try:
        float(str)
        return float(str)
    
    except ValueError:
        return False


def upload_image_to_imgbb(image_base64):

    url = "https://api.imgbb.com/1/upload"
    api_key = "37c8ea51af6c6c2e9bf543566c763169"
    expiration = "86400" # 1 month = 2624016 secs, 1 day = 86400

    payload = {
        "key": api_key,
        "image": image_base64,
        "expiration" : expiration
    }
    
    response = requests.post(url, payload)

    if response.status_code == 200:
        return response.json()['data']['url']
    else:
        return ""
