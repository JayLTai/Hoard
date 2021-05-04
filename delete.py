#!/usr/bin/env python
import sys
import platform
import time
import base64
import hashlib
import hmac

if int(platform.python_version_tuple()[0]) > 2:
 import urllib.request as urllib2
else:
 import urllib2

#TODO: UPDATE WITH YOUR KEYS :)
api_key = "Qp1EWdblPQ2Qm04iW+Vk7n4q60gcDTn51SF+/LXQWh7t7OcED4gQboX7"
api_secret = base64.b64decode("AmAEco2C/VWSXzvzNodfXM9QDaiq4pNjsPlayMWhXfQY1K+DotILZZaOims2Zq2fA4oU8svroW8WXrwzg11M6w==")

api_domain = "https://api.kraken.com"
api_path = "/0/private/"

#TODO: UPDATE WITH YOUR ENDPOINT & PARAMETERS :)
api_endpoint = "Balance" #{"error":[]} IS SUCCESS-EMPTY BALANCE
api_parameters = "" 

#EXAMPLES

#api_endpoint = "AddOrder" 
#api_parameters = "pair=xbteur&type=buy&ordertype=limit&price=5.00&volume=1" 

#api_endpoint = "AddOrder"
#api_parameters = "pair=xdgeur&type=buy&ordertype=market&volume=3000&userref=789" 

#api_endpoint = "Balance" #{"error":[]} IS SUCCESS-EMPTY BALANCE
#api_parameters = "" 

#api_endpoint = "QueryOrders" 
#api_parameters = "txid=OFUSL6-GXIIT-KZ2JDJ" 

#api_endpoint = "AddOrder"
#api_parameters = "pair=xdgusd&type=buy&ordertype=market&volume=5000"

#api_endpoint = "DepositAddresses"
#api_parameters = "asset=xbt&method=Bitcoin" 

#api_endpoint = "DepositMethods"
#api_parameters = "asset=eth" 

#api_endpoint = "WalletTransfer" 
#api_parameters = "asset=xbt&to=Futures Wallet&from=Spot Wallet&amount=0.0045" 

#api_endpoint = "TradesHistory"
#api_parameters = "start=1577836800&end=1609459200" 

#api_endpoint = "GetWebSocketsToken" 
#api_parameters = "" 

api_nonce = str(int(time.time()*1000))

api_postdata = api_parameters + "&nonce=" + api_nonce
api_postdata = api_postdata.encode('utf-8')

api_sha256Data = api_nonce.encode('utf-8') + api_postdata
api_sha256 = hashlib.sha256(api_sha256Data).digest()

api_hmacSha512Data = api_path.encode('utf-8') + api_endpoint.encode('utf-8') + api_sha256
api_hmacsha512 = hmac.new(api_secret, api_hmacSha512Data, hashlib.sha512)

api_sig = base64.b64encode(api_hmacsha512.digest())

api_url = api_domain + api_path + api_endpoint
api_request = urllib2.Request(api_url, api_postdata)
api_request.add_header("API-Key", api_key)
api_request.add_header("API-Sign", api_sig)
api_request.add_header("User-Agent", "Kraken REST API")
print("")
print("DEBUG DATA     : ")
print("api_url        : " + api_url)
print("api_endpoint   : " + api_endpoint)
print("api_parameters : " + api_parameters)
print("api_domain     : " + api_domain)
print("api_path       : " + api_path)
print("api_nonce      : " + api_nonce)
print("api_sig        : " + str(api_sig))
print("api_postdata   : " + str(api_postdata))
print("api_secret     : " + str(api_secret))
print("")

api_reply = urllib2.urlopen(api_request).read()
api_reply = api_reply.decode()


print("API JSON DATA:")
print(api_reply)
sys.exit(0)