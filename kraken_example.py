#!/usr/bin/env python

#IMPORT LIBRARIES
import sys
import platform
import time
import base64
import hashlib
import hmac
import websocket
import _thread as thread
import json
from datetime import datetime
import requests
import pdb

if int(platform.python_version_tuple()[0]) > 2:
	import urllib.request as urllib2
else:
	import urllib2

#DEFINE METHODS
def QueryPublicEndpoint(endpointName, inputParameters):
  jsonData = ""
  baseDomain = "https://api.kraken.com"
  publicPath = "/0/public/"
  apiEndpointFullURL = baseDomain + publicPath + endpointName + "?" + inputParameters
  response = requests.get(apiEndpointFullURL)
  jsonData = response.json()
  return jsonData

def QueryPrivateEndpoint(endpointName, inputParameters, apiPublicKey, apiPrivateKey):
  baseDomain = "https://api.kraken.com"
  privatePath = "/0/private/"

  apiEndpointFullURL = baseDomain + privatePath + endpointName
  nonce = str(int(time.time()*1000))
  apiPostBodyData = "nonce=" + nonce + inputParameters
  pdb.set_trace()
  apiPostData = inputParameters + "&nonce=" + nonce
  apiPostData = apiPostData.encode('utf-8')

  signature = CreateAuthenticationSignature(apiPrivateKey, 
                                            privatePath, 
                                            endpointName, 
                                            nonce, 
                                            apiPostData)
  jsonData = ""
  
  apiRequest = urllib2.Request(apiEndpointFullURL, apiPostData)
  apiRequest.add_header("API-Key", apiPublicKey)
  apiRequest.add_header("API-Sign", signature)
  apiRequest.add_header("User-Agent", "Kraken REST API")

  apiResponse = urllib2.urlopen(apiRequest).read()
  jsonData = apiResponse.decode()
             
  return jsonData

def CreateAuthenticationSignature(apiPrivateKey, 
                                  privatePath, 
                                  endpointName, 
                                  nonce, 
                                  apiPostData):

  pdb.set_trace()
  sha256Data = nonce.encode('utf-8') + apiPostData
  sha256Hash = hashlib.sha256(sha256Data).digest()

  hmacSha512Data = privatePath.encode('utf-8') + endpointName.encode('utf-8') + sha256Hash
  hmacSha512Hash = hmac.new(apiPrivateKey, hmacSha512Data, hashlib.sha512)

  signatureString = base64.b64encode(hmacSha512Hash.digest())
  return signatureString

def OpenAndStreamWebSocketSubscription(webSocketURL):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(webSocketURL,
                            on_message = WebSocketOnMessage,
                            on_error = WebSocketOnError,
                            on_close = WebSocketOnClose)
    ws.on_open = WebSocketOnOpen
    ws.run_forever()


def WebSocketOnMessage(ws, message):
    time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    print(time + ": " + message)

def WebSocketOnError(ws, error):
    time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    print(time + ": " + error)

def WebSocketOnClose(ws):
    time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    print(time + ": Websocket Closed!")

def WebSocketOnOpen(ws):
    def run():
            time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            print(time + ": Websocket Open!")
            ws.send(webSocketSubscription)
    thread.start_new_thread(run, ())

#RUN APP

#TODO: UPDATE WITH YOUR KEYS :)
apiPublicKey = "KPLlDob0WfygtiDknD0BG6TkuWDuEGC+zaNoYXry9nK4E0ayWmgubX1D"
apiPrivateKey = "j6tvLYKj7Pz5z6AhsG7Rd0sgN1+nyptOPt3g7A1X8MQYApfQh1AyM7VsTrVT6S4zqXEd1udU02NQNTTd0HFdoQ=="
apiPrivateKey = base64.b64decode(apiPrivateKey)

print("|=========================================|") 
print("|        KRAKEN.COM PYTHON TEST APP       |")
print("|=========================================|")
print()

##########
#
# Public REST API Examples
#
##########

publicResponse = ""
                
publicEndpoint = "SystemStatus"
publicInputParameters = ""

#MORE PUBLIC REST EXAMPLES
#*
#publicEndpoint = "AssetPairs"
#publicInputParameters = "pair=ethusd,xbtusd"

publicEndpoint = "Ticker"
publicInputParameters = "pair=ethusd"

#publicEndpoint = "Trades"
#publicInputParameters = "pair=ethusd&since=0"
#*

publicResponse = QueryPublicEndpoint(publicEndpoint, publicInputParameters)
print(publicResponse)

##########
#
# Private REST API Examples
#
##########

privateResponse = ""

privateEndpoint = "Balance"
privateInputParameters = ""

privateResponse = QueryPrivateEndpoint(privateEndpoint, privateInputParameters, apiPublicKey, apiPrivateKey)
print(privateResponse)

##########
#
# Public WebSocket API Examples
#
##########
# publicWebSocketURL = "wss://ws.kraken.com/"
# webSocketSubscription = "{ \"event\": \"subscribe\", \"subscription\": { \"name\": \"ticker\"}, \"pair\": [ \"XBT/EUR\",\"ETH/USD\" ]}"

#MORE PUBLIC WEBSOCKET EXAMPLES
#*
#webSocketSubscription = "{ \"event\": \"subscribe\", \"subscription\": { \"interval\": 1440, \"name\": \"ohlc\"}, \"pair\": [ \"XBT/EUR\"]}"
#webSocketSubscription = "{ \"event\": \"subscribe\", \"subscription\": { \"name\": \"spread\"}, \"pair\": [ \"XBT/EUR\",\"ETH/USD\" ]}"
#*

#OpenAndStreamWebSocketSubscription(publicWebSocketURL)

##########
#
# Private WebSocket API Examples
#
##########
# privateWebSocketURL = "wss://ws-auth.kraken.com/"
# webSocketSubscription = "{ \"event\": \"subscribe\", \"subscription\": { \"name\": \"ownTrades\", \"token\": \"#TOKEN#\"}}"

# #MORE PRIVATE WEBSOCKET EXAMPLES
# #*
# # #TOKEN# IS A PLACEHOLDER

# #webSocketSubscription = "{ \"event\": \"subscribe\", \"subscription\": { \"name\": \"openOrders\", \"token\": \"#TOKEN#\"}}"
# #webSocketSubscription = "{ \"event\": \"subscribe\", \"subscription\": { \"name\": \"balances\", \"token\": \"#TOKEN#\"}}"
# #addOrderExample =  "{\"event\":\"addOrder\",\"reqid\":1234,\"ordertype\":\"limit\",\"pair\":\"XBT/EUR\",\"token\":\"#TOKEN#\",\"type\":\"buy\",\"volume\":\"1\", \"price\":\"1.00\"}"
# #*

# #GET AND EXTRACT THE WEBSOCKET TOKEN FORM THE JSON RESPONSE
# webSocketRestResponseJSON = QueryPrivateEndpoint("GetWebSocketsToken", "", apiPublicKey, apiPrivateKey)
# jsonObject = json.loads(webSocketRestResponseJSON)
# webSocketToken = jsonObject['result']['token']

# #REPLACE PLACEHOLDER WITH TOKEN
# webSocketSubscription = webSocketSubscription.replace("#TOKEN#", webSocketToken)
# OpenAndStreamWebSocketSubscription(privateWebSocketURL)


                
