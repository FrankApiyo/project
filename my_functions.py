import base64
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import keys

#timestamp
def get_timestamp():
    unformatted_time = datetime.now()
    formatted_time = unformatted_time.strftime("%Y%m%d%H%M%S")
    return formatted_time

#generate password
def get_encoded_password():
    data_to_encode = keys.business_short_code + keys.lipa_na_mpesa_pass_key + get_timestamp()
    encoded_string = base64.b64encode(data_to_encode.encode())
    decoded_password = encoded_string.decode('utf-8')
    return decoded_password

#authentication
def generate_the_access_token():
    consumer_key = keys.consumer_key
    consumer_secret = keys.consumer_secret
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    json_response = r.json()
    access_token = json_response['access_token']
    return access_token