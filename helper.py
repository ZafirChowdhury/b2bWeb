from datetime import datetime

import requests

import key

def convert_html_date_time_to_python_datetime(date_time_str):
    return datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M') #'2015-01-02T00:00'


def check_is_float_and_convert(str):
    try:
        float(str)
        return float(str)
    
    except ValueError:
        return False


def upload_image_to_imgbb(image_base64):

    IMG_BB_URL = "https://api.imgbb.com/1/upload"
    EXPIRATION = "86400" # 1 month = 2624016 secs, 1 day = 86400

    payload = {
        "key": key.get_imgbb_api_key(),
        "image": image_base64,
        "expiration" : EXPIRATION
    }
    
    response = requests.post(IMG_BB_URL, payload)

    if response.status_code == 200:
        return response.json()['data']['url']
    else:
        return ""
