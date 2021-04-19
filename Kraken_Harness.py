# Crypto Facilities Ltd REST API v3

# Copyright (c) 2018 Crypto Facilities

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import time
import base64
import hashlib
import hmac
import json
import urllib.request as urllib2
import urllib.parse as urllib
import ssl
import pdb

class Kraken_Harness:
    def __init__(self, apiPublicKey="", apiPrivateKey="", timeout=10, checkCertificate=True, useNonce=True):
        self.apiPath = 'https://api.kraken.com'
        self.apiPublicKey = apiPublicKey
        self.apiPrivateKey = apiPrivateKey
        self.timeout = timeout
        self.nonce = 0
        self.checkCertificate = checkCertificate
        self.useNonce = useNonce

 # signs a message
    def sign_message(self, endpoint, postData, nonce=""):

        # Decode API private key from base64 format displayed in account management
        api_secret = base64.b64decode(self.apiPrivateKey)
        
        # Variables (API method, nonce, and POST data)
        api_path = endpoint
        api_nonce = str(int(time.time()*1000))
        api_post = "nonce=" + api_nonce + "&asset=" + postData
        
        # Cryptographic hash algorithms
        api_sha256 = hashlib.sha256(api_nonce.encode('utf-8') + api_post.encode('utf-8'))
        api_hmac = hmac.new(api_secret, api_path.encode('utf-8') + api_sha256.digest(), hashlib.sha512)
        
        # Encode signature into base64 format used in API-Sign value
        api_signature = base64.b64encode(api_hmac.digest())
        
        # API authentication signature for use in API-Sign HTTP header
        # print(api_signature.decode())
        return api_signature

    # creates a unique nonce
    def get_nonce(self):
        # https://en.wikipedia.org/wiki/Modulo_operation
        self.nonce = (self.nonce + 1) & 8191
        return str(int(time.time() * 1000)) + str(self.nonce).zfill(4)

    # sends an HTTP request
    def make_request_raw(self, requestType, endpoint, postUrl="", postBody=""):
        # create authentication headers
        # krakent requires the header to have an
        #   APIKey
        #   Nonce
        #   Authenticator
        postData = postUrl + postBody

        if self.useNonce:
            nonce = self.get_nonce()
            signature = self.sign_message(endpoint, postData, nonce=nonce)
            authentHeaders = {"APIKey": self.apiPublicKey,
                              "Nonce": nonce, "API-Sign": signature}
        else:
            signature = self.sign_message(endpoint, postData)
            authentHeaders = {
                "APIKey": self.apiPublicKey, "API-Sign": signature}

        authentHeaders["User-Agent"] = "cf-api-python/1.0"

        # create request
        if postUrl != "":
            url = self.apiPath + endpoint + "?" + postUrl
        else:
            url = self.apiPath + endpoint

        request = urllib2.Request(url, str.encode(postBody), authentHeaders)
        request.get_method = lambda: requestType

        # read response
        if self.checkCertificate:
            response = urllib2.urlopen(request, timeout=self.timeout)
        else:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            response = urllib2.urlopen(
                request, context=ctx, timeout=self.timeout)

        # return
        return response

    # sends an HTTP request and read response body
    def make_request(self, requestType, endpoint, postUrl="", postBody=""):
        return self.make_request_raw(requestType, endpoint, postUrl, postBody).read().decode("utf-8")

    def process_response(self, response):
        """
        processes a response so we either raise a hard error exception or return easily parsable responses
        Args:
            response : a utf-8 string response from the REST call returns
        Returns:
            a dictionary with the relevant data pulled from the response
        """
        response = json.loads(response)
        if not response['error']:
           result = response['result'] 
        else:
            raise RuntimeError('Got REST call error : {}'.format(response['error']))
        return result


    ######################
    #    api functions   #
    ######################

    #for more information visit: https://www.kraken.com/en-us/features/api
    #all functions here can be found in the link above with corresponding REST docs

    def get_servertime(self):
        endpoint = '/0/public/Time'
        return self.process_response(self.make_request('GET', endpoint))

    def get_systemstatus(self):
        endpoint = '/0/public/SystemStatus'
        return self.process_response(self.make_request('GET', endpoint))