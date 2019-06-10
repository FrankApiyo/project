import requests
from my_functions import get_timestamp,get_encoded_password,generate_the_access_token
import keys




def lipa_na_mpesa(phone_number, amount):
    the_timestamp = get_timestamp()
    the_password  = get_encoded_password()
    the_access_token = generate_the_access_token()
    access_token = the_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = { "Authorization": "Bearer %s" % access_token }
    request = {
    "BusinessShortCode": keys.business_short_code,
    "Password": the_password,
    "Timestamp": the_timestamp,
    "TransactionType": "CustomerPayBillOnline",
    "Amount": amount,
    "PartyA": phone_number,
    "PartyB": keys.business_short_code,
    "PhoneNumber": phone_number,
    "CallBackURL": "https://emmicode.pythonanywhere.com/api/payments/lnm/",
    "AccountReference": "matrips",
    "TransactionDesc": "Pay for a matatu ticket"
    }

    response = requests.post(api_url, json = request, headers=headers)
    print (response.text)