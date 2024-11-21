import requests

url = "https://api.imgbb.com/1/upload"
api_key = "37c8ea51af6c6c2e9bf543566c763169"
expiration = "86400" # 1 month = 2624016 secs, 1 day = 86400

def upload_image_to_imgbb(image_base64):

    payload = {
        "key": api_key,
        "image": image_base64,
        "expiration" : expiration
    }
    
    response = requests.post(url, payload)

    print(response.json())
    
    if response.status_code == 200:
        return response.json()['data']['url']
    else:
        return ""
