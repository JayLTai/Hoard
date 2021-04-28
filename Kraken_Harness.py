# reference : https://github.com/CryptoFacilities/REST-v3-Python/blob/master/cfRestApiV3.py

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
    def __init__(self, apiPublicKey="", apiPrivateKey="", timeout=10):
        self.apiPath = 'https://api.kraken.com'
        self.apiPublicKey = apiPublicKey
        self.apiPrivateKey = apiPrivateKey
        self.timeout = timeout
        self.nonce = 0

 # signs a message
 # https://support.kraken.com/hc/en-us/articles/360022635592-Generate-authentication-strings-REST-API-\
 # https://support.kraken.com/hc/en-us/articles/360029054811-What-is-the-authentication-algorithm-for-private-endpoints-
    def sign_message(self, endpoint, postData, nonce=""):
        
        # apiPostData = "&nonce=" + nonce + postData
        apiPostData = 'nonce=' + nonce + '&' + postData

        # Decode API private key from base64 format displayed in account management
        api_secret = base64.b64decode(self.apiPrivateKey)

        # Cryptographic hash algorithms
        sha256_hash = hashlib.sha256(nonce.encode('utf-8') + apiPostData.encode('utf-8')).digest()

        hmac_sha256_data = endpoint.encode('utf-8') + sha256_hash
        hmac_sha256_hash = hmac.new(api_secret, hmac_sha256_data, hashlib.sha512)
        
        # Encode signature into base64 format used in API-Sign value
        api_signature = base64.b64encode(hmac_sha256_hash.digest())
        # pdb.set_trace()
        
        # API authentication signature for use in API-Sign HTTP header
        return api_signature

    # creates a unique nonce
    def get_nonce(self):
        # https://en.wikipedia.org/wiki/Modulo_operation
        self.nonce = (self.nonce + 1) & 8191
        return str(int(time.time() * 1000)) + str(self.nonce).zfill(4)

    # sends an HTTP request
    def make_request(self, endpoint, postUrl=""):
        # create authentication headers
        # krakent requires the header to have an
        #   APIKey
        #   Nonce
        #   Authenticator

        nonce = self.get_nonce()
        signature = self.sign_message(endpoint, postUrl, nonce=nonce)
        authentHeaders = {"API-Key": self.apiPublicKey,
                            "nonce": nonce, "API-Sign": signature}

        authentHeaders["User-Agent"] = "Kraken REST API"

        # create request
        if postUrl != "":
            url = self.apiPath + endpoint + "?" + postUrl
        else:
            url = self.apiPath + endpoint
        request = urllib2.Request(url, str.encode(postUrl), authentHeaders)
        response = urllib2.urlopen(request, timeout=self.timeout)

        # return
        return response.read().decode("utf-8")

    
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

    def build_data(self,data):
        """
        processes a dictionary object into a json data object to be sent with a REST cal
        Args:
            data : a dictionary object to be converted into a json object
        Returns:
            the json object
        """
        return json.dumps(data)

    def make_postURL(self,data):
        """
        process a dictionary of {parameter names : parameter data} in order to 
        generate appropriate postURL data to add to the REST call 
        Args:
            data {parameter names : parameter data} : a dictionary representing the postURLs
                                                      parameter names and data
        Returns:
            string representing the complete postURL to be added to the end of a REST call

        """
        postURL = ''
        for key,item in data.items():
        #if the item is not an empty string
            if not not item:
                if not postURL:
                    postURL = '{k}={i}'.format(k=key, i=item)
                else:
                    postURL = postURL + '&{k}={i}'.format(k=key, i=item)
        return postURL
        
    ######################
    #    api functions   #
    ######################

    #for more information visit: https://www.kraken.com/en-us/features/api
    #all functions here can be found in the link above with corresponding REST docs
    # api_private_get = {"accounts", "openorders", "fills", "openpositions", "transfers", "notifications", "historicorders", "recentorders"}
    # api_private_post = {"transfer", "sendorder", "cancelorder", "cancelallorders", "cancelallordersafter", "batchorder", "withdrawal"}


    def get_servertime(self):
        endpoint = '/0/public/Time'
        return self.process_response(self.make_request(endpoint))

    def get_systemstatus(self):
        endpoint = '/0/public/SystemStatus'
        return self.process_response(self.make_request(endpoint))

    def get_assetinfo(self, info = "", aclass = "", asset = ""):
        """
        info default = all info
        aclass default = currency
        asset default = all for given asset class
        """
        endpoint = '/0/public/Assets'
        data = dict(zip(['info','aclass','asset'],[info,aclass,asset]))
        postURL = self.make_postURL(data)
        return self.process_response(self.make_request(endpoint, postUrl = postURL))

    def get_assetpairs(self,info = "", pair = ""):
        """
        info = all info (default) : | leverage | fees | margin
        pair = comma delimited list of asset pairs to get info from (default = all)
                ie: ETHUSD, BTCUSD
        """
        endpoint = '/0/public/AssetPairs'
        data = dict(zip(['info','pair'],[info,pair]))
        postURL = self.make_postURL(data)
        return self.process_response(self.make_request(endpoint, postUrl = postURL))

    def get_tickerinfo(self,pair = ""):
        """
        pair = comma delimited list of asset pairs to get info from 
        """
        endpoint = '/0/public/Ticker'
        data = dict(zip(['pair'],[pair]))
        postURL = self.make_postURL(data)
        return self.process_response(self.make_request(endpoint, postUrl = postURL))

    def get_ohlc(self,pair = "", interval = "", since = ""):
        """
        OHLC = Open, High, Low, Close
        pair = asset pair to collect OHLC
        interval (optional) = time frame interval in minutes 1 (default), 5, 15, 30, 60, 240, 1440, 10080, 21600
        since (optional.  exclusive) = return committed OHLC data since given id 
        """
        endpoint = '/0/public/OHLC'
        data = dict(zip(['pair','interval','since'],[pair,interval,since]))
        postURL = self.make_postURL(data)
        return self.process_response(self.make_request(endpoint, postUrl = postURL))

    def get_orderbook(self,pair = "", count = ""):
        """
        pair = asset pair to get market depth for
        count = maximum number of asks/bids (optional)
        Returns:
            <pair_name> = pair name
            asks = ask side array of array entries(<price>, <volume>, <timestamp>)
            bids = bid side array of array entries(<price>, <volume>, <timestamp>)
        """
        endpoint = '/0/public/Depth'
        data = dict(zip(['pair','count'],[pair,count]))
        postURL = self.make_postURL(data)
        return self.process_response(self.make_request(endpoint, postUrl = postURL))

    def get_recenttrades(self,pair = "", since = ""):
        """
        pair = asset pair to get trade data for
        since = return trade data since given id (optional.  exclusive)
        Returns:
            <pair_name> = pair name
            array of array entries(<price>, <volume>, <time>, <buy/sell>, <market/limit>, <miscellaneous>)
            last = id to be used as since when polling for new trade data
        """
        endpoint = '/0/public/Trades'
        data = dict(zip(['pair','since'],[pair,since]))
        postURL = self.make_postURL(data)
        return self.process_response(self.make_request(endpoint, postUrl = postURL))

    def get_recentspread(self,pair = "", since = ""):
        """
        pair = asset pair to get spread data for
        since = return spread data since given id (optional.  inclusive)
        Returns:
            <pair_name> = pair name
            array of array entries(<time>, <bid>, <ask>)
            last = id to be used as since when polling for new spread data
        """
        endpoint = '/0/public/Spread'
        data = dict(zip(['pair','since'],[pair,since]))
        postURL = self.make_postURL(data)
        return self.process_response(self.make_request(endpoint, postUrl = postURL))


    ############# PRIVATE FUNCTIONS ##############

    def get_accountbalance(self):
        """
        Returns:
            array of asset names and balance amount
        """
        endpoint = '/0/private/Balance'
        return self.make_request(endpoint)
        # return self.process_response(self.make_request(endpoint))

    def get_tradebalance(self,aclass = "", asset = ""):
        """
        aclass = asset class (optional):
            currency (default)
        asset = base asset used to determine balance (default = ZUSD)
        Returns: array of trade balance info
            eb = equivalent balance (combined balance of all currencies)
            tb = trade balance (combined balance of all equity currencies)
            m = margin amount of open positions
            n = unrealized net profit/loss of open positions
            c = cost basis of open positions
            v = current floating valuation of open positions
            e = equity = trade balance + unrealized net profit/loss
            mf = free margin = equity - initial margin (maximum margin available to open new positions)
            ml = margin level = (equity / initial margin) * 100
        """
        endpoint = '/0/private/TradeBalance'
        data = dict(zip(['aclass','asset'],[aclass,asset]))
        postURL = self.make_postURL(data)
        return self.process_response(self.make_request(endpoint, postUrl = postURL))
