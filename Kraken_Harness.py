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
        if not response['error'] and response:
            try:
                result = response['result']
            except KeyError:
                print(" +++++++ response from server received.......empty result............. +++++++")
                print(" +++++++ did you call get account balance on an account wihtout money? +++++++")
                return ""
        else:
            raise RuntimeError('Got Error response from Kraken REST response : {}'.format(response['error']))
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

    #for more information visit: https://docs.kraken.com/rest/
    #all functions here can be found in the link above with corresponding REST docs
    # api_private_get = {"accounts", "openorders", "fills", "openpositions", "transfers", "notifications", "historicorders", "recentorders"}
    # api_private_post = {"transfer", "sendorder", "cancelorder", "cancelallorders", "cancelallordersafter", "batchorder", "withdrawal"}

    ########## PUBLIC FUNCTIONS ##########

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


    ############# PRIVATE USER DATA FUNCTIONS ##############

    def get_accountbalance(self):
        """
        Returns:
            array of asset names and balance amount
        """
        api_path = '/0/private/'
        endpoint = 'Balance'
        return self.process_response(self.make_request(api_path, endpoint))

    def get_tradebalance(self,asset = ""):
        #getting internal error from this, not sure why yet, email support
        """
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
        data = dict(zip(['asset'],[asset]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data = post_data))

    def get_tradeshistory(self, type = ""):
            api_path = '/0/private/'
            endpoint = 'TradesHistory'
            return self.process_response(self.make_request(api_path, endpoint, post_data=""))


    ############# PRIVATE USER FUNDING AND TRADING FUNCTIONS ##############

    def add_order(self,  ordertype, type, pair, userref = "", volume = "",
                  price = "", price2 = "", leverage = "", oflags = "", starttm = "",
                  expiretm = "", close_ordertype = "", close_price = "", close_price2 = "",
                  trading_agreement = "", validate = False):
        """
        Args:
            userref: (string) user reference ID
                    Optional user specified integer id that can be used to assosciated with
                    any number of orders
            ordertype: (string) REQUIRED - Order Type
                    Enum: "market" "limit" - "stop-loss" - "take-profit" - "stop-loss-limit"
                    "take-profit-limit" - "settle-position"
            type: (string) REQUIRED - order direction : buy or sell
                    Enum: "buy" - "sell"
            volume: (string) - order quantity in terms of the base asset
                    Note: Volume can be specified as 0 for closing margin orders to automatically
                    fill the requisite quantity.
            pair: (string) REQUIRED -  Asset pair ID or altname
            price: (string) - Price
                    Limit price for - limit - orders
                    trigger price for - stop-loss, stop-loss-limit, take-profit, take-profit-limit - orders
            price2: (string) - Secondary price
                    Limit price for - stop-loss-limit, take-profit-limit - orders
                    Note: Either price or price2 can be preceded by +, -, or # to specify the order price as
                    an offset relative to the last traded price.
                    + adds the amount
                    - subtracts the amount
                    # will either add or subtract the amount to the last traded price, depending on direction and order type used.
                    Relative prices can be suffixed with a % to signify the relative amount as a percentage.
            leverage: (string) amount of leverage desired
                    default = none
            oflags: (string) comma delimited list of order flags
                    "post" post-only order (available when ordertype = limit)
                    "fcib" prefer fee in base currency (default if selling)
                    "fciq" prefer fee in quote currency (default if buying, mutually exclusive with fcib)
                    "nompp" disable market price protection for market orders
            starttm: (string) scheduled start time of order can be specified as a specific time stamp or number of seconds in future
                    "0" now (default)
                    "+<n>" schedule start time seconds from now
                    "<n>" = unix timestamp of start time
            expiretm: (string) order expiration time, follows same rules as starttm
                    "0" no expiration (default)
                    "+<n>" = expire seconds from now, minimum 5 seconds
                    "<n>" = unix timestamp of expiration time
            closeordertype: (string) conditional close order type see: https://support.kraken.com/hc/en-us/articles/360038640052-Conditional-Close
                    Enum: "limit" "stop-loss" "take-profit" "stop-loss-limit" "take-profit-limit"
            close_price: (string) conditional close order price - Same as price
            close_price2: (string) conditional close order price2  - Same as price2
            trading_agreement: (string) Value is "agree" - Required in Germany ?????
                    https://support.kraken.com/hc/en-us/articles/360000920026--Trading-agreement-required-error-for-German-residents
            validate: (boolean)
                    true - submit order
                    false - (DEFAULT) do not submit order, just validate parameters
        Returns:
            descr : description
                order : order execution description
                close : order close description
            txid : transaction id
        """
        api_path = '/0/private/'
        endpoint = 'AddOrder'
        data = dict(zip(['userref', 'ordertype','type','volume','pair','pair',
                         'price','price2','leverage','oflags','starttm','expiretm',
                         'close[ordertype]','close[price]','close[price2]',
                         'trading_agreement','validate'],
                        [userref, ordertype, type, volume, pair, price, price2,
                         leverage, oflags, starttm, expiretm, close_ordertype,
                         close_price, close_price2, trading_agreement, validate]))
        post_data = self.make_post_data(data)
        # return self.process_response(self.make_request(api_path, endpoint, post_data = post_data))
        return self.make_request(api_path, endpoint, post_data = post_data)

    def cancel_order(self, txid):
        """

        Args:
            txid: (string or integer) REQUIRED - Open order transaction ID (txid) or user reference (userref)

        Returns:
            count: number of orders canceled(?)
        """
        api_path = '/0/private/'
        endpoint = 'CancelOrder'
        data = dict(zip(['txid'],[txid]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data = post_data))

    def cancle_allorders(self):
        """

        Returns:
            count: number of orders canceled(?)
        """
        api_path = '/0/private/'
        endpoint = 'CancelAll'
        return self.process_response(self.make_request(api_path, endpoint))

    def cancel_allordersafter(self, timeout):
        """
        CancelAllOrdersAfter provides a "Dead Man's Switch" mechanism to protect the client
        from network malfunction, extreme latency or unexpected matching engine downtime.
        The client can send a request with a timeout (in seconds), that will start a countdown
        timer which will cancel all client orders when the timer expires. The client has to keep
        sending new requests to push back the trigger time, or deactivate the mechanism by
        specifying a timeout of 0. If the timer expires, all orders are cancelled and then the
        timer remains disabled until the client provides a new (non-zero) timeout.

        The recommended use is to make a call every 15 to 30 seconds,
        providing a timeout of 60 seconds. This allows the client to keep the orders in place
        in case of a brief disconnection or transient delay, while keeping them safe in case of
        a network breakdown. It is also recommended to disable the timer ahead of regularly
        scheduled trading engine maintenance (if the timer is enabled, all orders will be
        cancelled when the trading engine comes back from downtime - planned or otherwise).
        Args:
            timeout: (int) REQUIRED - Duration (in seconds) to set/extend the timer by

        Returns:
            currenttime : time of response sent
            triggertime : time of trigger of cancel
        """
        api_path = '/0/private/'
        endpoint = 'CancelAllOrdersAfter'
        data = dict(zip(['timeout']),[timeout])
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data = post_data))

    def get_depositmethods(self, asset):
        """
        Args:
            asset: (string) REQUIRED - asset being deposited
        Returns:
            method:
            limit:
            fee:
            gen-address
        """
        api_path = '/0/private/'
        endpoint = 'DepositMethods'
        data = dict(zip(['asset']), [asset])
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_depositaddress(self, asset, method, new = True):
        """
        Args:
            asset: (string) REQUIRED - asset being deposited
            method: (string) REQUIRED - name of the deposit method
            new: (bool) wether or not to generate a new address
        Returns:
            address:
            expiretm:
            new:
        """
        api_path = '/0/private/'
        endpoint = 'DepositAddresses'
        data = dict(zip(['asset','method','new']), [asset,method,new])
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_depositstatus(self, asset, method = ""):
        """
        Gets status and information of most recent deposit of given asset
        Args:
            asset: (string) REQUIRED - asset being deposited
            method: (string) name of the deposit method
        Returns:
            method:
            aclass:
            asset:
            refid:
            txid:
            info:
            amount:
            fee:
            time:
            status:
        """
        api_path = '/0/private/'
        endpoint = 'DepositMethods'
        data = dict(zip(['asset','method']), [asset,method])
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_withdrawalinfo(self, asset, key, amount):
        """
        Retrieve fee information about potential withdrawals for a particular asset, key and amount.
        Args:
            asset: (string) asset being withdrawn
            key: (string) withdrawal key name, as set up on your account
            amount: (string) amount to be withdrawn

        Returns:
            method:
            limit:
            amount:
            fee:
        """
        api_path = '/0/private/'
        endpoint = 'WithdrawInfo'
        data = dict(zip(['asset','key','amount'],[asset,key,amount]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def withdraw_funds(self, asset, key, amount):
        """
        Retrieve fee information about potential withdrawals for a particular asset, key and amount.
        Args:
            asset: (string) asset being withdrawn
            key: (string) withdrawal key name, as set up on your account
            amount: (string) amount to be withdrawn

        Returns:
            refid:
        """
        api_path = '/0/private/'
        endpoint = 'Withdraw'
        data = dict(zip(['asset','key','amount'],[asset,key,amount]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_withdrawstatus(self, asset, method):
        """
        Retrieve fee information about potential withdrawals for a particular asset, key and amount.
        Args:
            asset: (string) asset being withdrawn
            method: (string) name of withdrawal method

        Returns:
            method:
            aclass:
            asset:
            refid:
            txid:
            info:
            amount:
            fee:
            time:
            status:
            status-prop:
        """
        api_path = '/0/private/'
        endpoint = 'WithdrawStatus'
        data = dict(zip(['asset','method'],[asset,method]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def cancel_withdraw(self, asset, refid):
        """
        Retrieve fee information about potential withdrawals for a particular asset, key and amount.
        Args:
            asset: (string) asset being withdrawn
            refid: (string) withdrawal reference ID

        Returns:
            result:
        """
        api_path = '/0/private/'
        endpoint = 'WithdrawlCancel'
        data = dict(zip(['asset', 'refid'], [asset, refid]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def request_wallet_transfer(self, asset, amount, frm = "Spot Wallet", to = "Futures Wallet"):
        """
        Transfer from Kraken spot wallet to Kraken Futures holding wallet. Note that a transfer in the other direction
        must be requested via the Kraken Futures API endpoint.
        Args:
            asset: (string) REQUIRED - Asset to transfer (asset ID or altname)
            frm: (string) REQUIRED - value : "Spot Wallet"
            to: (string) REQUIRED - value : "Futures Wallet"
            amount: (string) REQUIRED - amount to transfer

        Returns:
            refid:
        """
        api_path = '/0/private/'
        endpoint = 'WalletTransfer'
        data = dict(zip(['asset', 'from', 'to', 'amount'], [asset, frm, to, amount]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))