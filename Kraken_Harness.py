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
    def __init__(self, api_publickey="", api_privatekey="", timeout=10):
        self.api_domain = 'https://api.kraken.com'
        self.api_publickey = api_publickey
        self.api_privatekey = api_privatekey
        self.timeout = timeout
        self.nonce = 0

 # signs a message
 # https://support.kraken.com/hc/en-us/articles/360022635592-Generate-authentication-strings-REST-API-\
 # https://support.kraken.com/hc/en-us/articles/360029054811-What-is-the-authentication-algorithm-for-private-endpoints-
    def sign_message(self, endpoint, api_postdata, api_path, nonce=""):

        # Decode API private key from base64 format displayed in account management
        # api_secret = base64.b64decode(self.api_privatekey)
        api_secret = self.get_apisecret()

        # Cryptographic hash algorithms
        sha256_data = nonce.encode('utf-8') + api_postdata
        sha256_hash = hashlib.sha256(sha256_data).digest()

        print("endpoint input : " + str(endpoint) + "---------")
        hmac_sha256_data = api_path.encode('utf-8') + endpoint.encode('utf-8') + sha256_hash
        hmac_sha256_hash = hmac.new(api_secret, hmac_sha256_data, hashlib.sha512)
        
        # Encode signature into base64 format used in API-Sign value
        api_signature = base64.b64encode(hmac_sha256_hash.digest())
   
        # API authentication signature for use in API-Sign HTTP header
        return api_signature

    # creates a unique nonce
    def get_nonce(self):
        self.nonce = str(int(time.time()*1000))
        return self.nonce

    def get_apisecret(self):
        return base64.b64decode(self.api_privatekey)

    # sends an HTTP request
    def make_request(self, api_path, endpoint, post_data="",nonce=""):
        # create authentication headers
        # krakent requires the header to have an
        #   APIKey
        #   Nonce
        #   Authenticator

        if not nonce:
            nonce = self.get_nonce()

        api_postdata = post_data + '&nonce=' + nonce
        api_postdata = api_postdata.encode('utf-8')

        signature = self.sign_message(endpoint = endpoint, api_postdata = api_postdata, api_path = api_path, nonce=nonce)

        # create request
        url = self.api_domain + api_path + endpoint
        request = urllib2.Request(url, api_postdata)
        request.add_header("API-Key", self.api_publickey)
        request.add_header("API-Sign", signature)
        request.add_header("User-Agent", "Kraken Rest API")
        response = urllib2.urlopen(request, timeout=self.timeout)

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

    def make_post_data(self,data):
        """
        process a dictionary of {parameter names : parameter data} in order to 
        generate appropriate post_data data to add to the REST call 
        Args:
            data {parameter names : parameter data} : a dictionary representing the post_datas
                                                      parameter names and data
        Returns:
            string representing the complete post_data to be added to the end of a REST call

        """
        post_data = ''
        for key,item in data.items():
        #if the item is not an empty string
            if not not item:
                if not post_data:
                    post_data = '{k}={i}'.format(k=key, i=item)
                else:
                    post_data = post_data + '&{k}={i}'.format(k=key, i=item)
        return post_data
        
    ######################
    #    api functions   #
    ######################

    #for more information visit: https://www.kraken.com/en-us/features/api
    #all functions here can be found in the link above with corresponding REST docs
    # api_private_get = {"accounts", "openorders", "fills", "openpositions", "transfers", "notifications", "historicorders", "recentorders"}
    # api_private_post = {"transfer", "sendorder", "cancelorder", "cancelallorders", "cancelallordersafter", "batchorder", "withdrawal"}


    def get_servertime(self):
        api_path = '/0/public/'
        endpoint = 'Time'
        return self.process_response(self.make_request(api_path, endpoint))

    def get_systemstatus(self):
        api_path = '/0/public/'
        endpoint = 'SystemStatus'
        return self.process_response(self.make_request(api_path, endpoint))

    def get_assetinfo(self, info = "", aclass = "", asset = ""):
        """
        info default = all info
        aclass default = currency
        asset default = all for given asset class
        """
        api_path = '/0/public/'
        endpoint = 'Assets'
        data = dict(zip(['info','aclass','asset'],[info,aclass,asset]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data = post_data))

    def get_assetpairs(self,info = "", pair = ""):
        """
        info = all info (default) : | leverage | fees | margin
        pair = comma delimited list of asset pairs to get info from (default = all)
                ie: ETHUSD, BTCUSD
        """
        api_path = '/0/public/'
        endpoint = 'AssetPairs'
        data = dict(zip(['info','pair'],[info,pair]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data = post_data))

    def get_tickerinfo(self,pair = ""):
        """
        pair = comma delimited list of asset pairs to get info from 
        """
        api_path = '/0/public/'
        endpoint = 'Ticker'
        data = dict(zip(['pair'],[pair]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data = post_data))

    def get_ohlc(self,pair = "", interval = "", since = ""):
        """
        OHLC = Open, High, Low, Close
        pair = asset pair to collect OHLC
        interval (optional) = time frame interval in minutes 1 (default), 5, 15, 30, 60, 240, 1440, 10080, 21600
        since (optional.  exclusive) = return committed OHLC data since given id 
        """
        api_path = '/0/public/'
        endpoint = 'OHLC'
        data = dict(zip(['pair','interval','since'],[pair,interval,since]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data = post_data))

    def get_orderbook(self,pair = "", count = ""):
        """
        pair = asset pair to get market depth for
        count = maximum number of asks/bids (optional)
        Returns:
            <pair_name> = pair name
            asks = ask side array of array entries(<price>, <volume>, <timestamp>)
            bids = bid side array of array entries(<price>, <volume>, <timestamp>)
        """
        api_path = '/0/public/'
        endpoint = 'Depth'
        data = dict(zip(['pair','count'],[pair,count]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data = post_data))

    def get_recenttrades(self,pair = "", since = ""):
        """
        pair = asset pair to get trade data for
        since = return trade data since given id (optional.  exclusive)
        Returns:
            <pair_name> = pair name
            array of array entries(<price>, <volume>, <time>, <buy/sell>, <market/limit>, <miscellaneous>)
            last = id to be used as since when polling for new trade data
        """
        api_path = '/0/public/'
        endpoint = 'Trades'
        data = dict(zip(['pair','since'],[pair,since]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data = post_data))

    def get_recentspread(self,pair = "", since = ""):
        """
        pair = asset pair to get spread data for
        since = return spread data since given id (optional.  inclusive)
        Returns:
            <pair_name> = pair name
            array of array entries(<time>, <bid>, <ask>)
            last = id to be used as since when polling for new spread data
        """
        api_path = '/0/public/'
        endpoint = 'Spread'
        data = dict(zip(['pair','since'],[pair,since]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data = post_data))


    ############# PRIVATE FUNCTIONS ##############

    def get_accountbalance(self):
        """
        Returns:
            array of asset names and balance amount
        """
        api_path = '/0/private/'
        endpoint = 'Balance'
        return self.process_response(self.make_request(api_path, endpoint))
        # return self.make_request(api_path, endpoint)

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
        api_path = '/0/private/'
        endpoint = 'TradeBalance'
        data = dict(zip(['aclass','asset'],[aclass,asset]))
        post_data = self.make_post_data(data)
        print(post_data)
        return self.process_response(self.make_request(api_path, endpoint, post_data = post_data))
