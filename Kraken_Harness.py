import time
import base64
import hashlib
import hmac
import json
import urllib.request as urllib2
import requests
import zipfile
import os
import pdb


class KrakenHarness():
    # enums(?) for pst and get paths
    _GET = '/0/public/'
    _POST = '/0/private/'

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
        self.nonce = str(int(time.time() * 1000))
        return self.nonce

    def get_apisecret(self):
        return base64.b64decode(self.api_privatekey)

    # sends an HTTP request
    def make_request(self, api_path, endpoint, post_data="", nonce="", data_dict = {}):
        # create authentication headers
        # krakent requires the header to have an
        #   APIKey
        #   Nonce
        #   Authenticator

        if not nonce:
            nonce = self.get_nonce()
        data_dict["nonce"] = nonce
        api_postdata = post_data + '&nonce=' + nonce
        params = bytes(api_postdata, 'utf-8')
        api_postdata = api_postdata.encode('utf-8')

        signature = self.sign_message(endpoint=endpoint, api_postdata=api_postdata, api_path=api_path, nonce=nonce)

        headers = {
            'API-Key': self.api_publickey,
            'API-Sign': signature,
            'User-Agent': "Kraken Rest API"
        }

        # create request
        url = self.api_domain + api_path + endpoint
        # request = urllib2.Request(url, api_postdata)
        # request.add_header("API-Key", self.api_publickey)
        # request.add_header("API-Sign", signature)
        # request.add_header("User-Agent", "Kraken Rest API")
        # response = urllib2.urlopen(request, timeout=self.timeout)

        #requests library test
        if api_path == KrakenHarness._GET:
            response = requests.get(url, params=params, headers=headers)
        elif api_path == KrakenHarness._POST:
            response = requests.post(url, headers=headers, data = data_dict )

        try:
            # return response.read().decode("utf-8")
            return response.content
        except UnicodeDecodeError:
            print(" !!!!! was not able to decode REST result, did you call get_report()? !!!!! ")
            print(" returning raw result ")
            return response

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

    def build_data(self, data):
        """
        processes a dictionary object into a json data object to be sent with a REST cal
        Args:
            data : a dictionary object to be converted into a json object
        Returns:
            the json object
        """
        return json.dumps(data)

    def make_post_data(self, data):
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
        for key, item in data.items():
            # if the item is not an empty string then add it to the post_datwa
            if not not item:
                if not post_data:
                    post_data = '{k}={i}'.format(k=key, i=item)
                else:
                    post_data = post_data + '&{k}={i}'.format(k=key, i=item)
        return post_data

    ######################
    #    api functions   #
    ######################

    # for more information visit: https://docs.kraken.com/rest/
    # all functions here can be found in the link above with corresponding REST docs
    # api_private_get = {"accounts", "openorders", "fills", "openpositions",
    #                       "transfers", "notifications", "historicorders", "recentorders"}
    # api_private_post = {"transfer", "sendorder", "cancelorder", "cancelallorders",
    #                       "cancelallordersafter", "batchorder", "withdrawal"}

    ########## PUBLIC FUNCTIONS ##########

    def get_servertime(self):
        """
        Get the serves time
        Returns:
            unixtime : (int)
            rfc1123  : (string) "Sun, 21 Mar 21 14:23:14 +0000"
        """
        api_path = KrakenHarness._GET
        endpoint = 'Time'
        return self.process_response(self.make_request(api_path, endpoint))

    def get_systemstatus(self):
        """
        get the current system status or trading mode
        Returns:
            status : (string)
            timestamp : (string) "2021-03-21T15:33:02Z"
        """
        api_path = KrakenHarness._GET
        endpoint = 'SystemStatus'
        return self.process_response(self.make_request(api_path, endpoint))

    def get_assetinfo(self, aclass="", asset=""):
        """
        Get information about the assets that are available for deposit, withdrawal, trading and staking
        Args:
            aclass : (string) asset class
                "currency"
            asset : (string) comma delimited list of assets to get info on
                "all" - default

        Returns:
            asset name (string) : {
                aclass :
                altname :
                decimals : (int)
                display_decimals : (int)
            }
        """
        api_path = KrakenHarness._GET
        endpoint = 'Assets'
        data = dict(zip(['aclass', 'asset'], [aclass, asset]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_assetpairs(self, info="", pair=""):
        """
        Get tradable asset pairs
        Args:
            info: (string) info to retrieve
                    "info" - default
                    "leverage"
                    "fees"
                    "margin"
            pair:(string) Asset pairs to get data for
                    ex : "XXBTCZUSD,XETHXXB"

        Returns:
            pair name (string) : {
                altname :
                wsname :
                aclass_base :
                base :
                aclass_quote :
                quote :
                lot :
                pair_decimals : (int)
                lot_decimals : (int)
                lot_multiplier : (int)
                leverage_buy : [int]
                leverage_sell : [int]
                fees : [[int]]
                fees : [[int]]
                fee_volume_currency :
                margin_call : (int)
                margin_stop : (int)
                ordermin :
            }
        """
        api_path = KrakenHarness._GET
        endpoint = 'AssetPairs'
        data = dict(zip(['info', 'pair'], [info, pair]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_tickerinfo(self, pair=""):
        """
        Get info of given ticker (greeks??)
        Note: Today's prices start at midnight UTC
        Args:
            pair: (string) asset pair to get data for
                    ex : XBTUSD

        Returns:
            ticker pair name (string) : {
                a : [string]
                b : [string]
                c : [string]
                v : [string]
                p : [string]
                t : [int]
                l : [string]
                h : [string]
                o : [string]
            }

        """
        api_path = KrakenHarness._GET
        endpoint = 'Ticker'
        data = dict(zip(['pair'], [pair]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_ohlc(self, pair, interval="", since=""):
        """
        Note: the last entry in the OHLC array is for the current, not-yet-committed frame and will always be present,
        regardless of the value of 'since'
        Args:
            pair: (string) REQUIRED - Asset pair to get data for
                    ex : "XBTUSD"
            interval: (int) time frame interval in minutes
                    default = 1
                    1
                    5
                    15
                    30
                    60
                    240
                    1440
                    10080
                    21600
            since:  (int) Return commited OHLC data since given ID
                    ex : 1548111600

        Returns: ( needa figure out what this means )
            asset name (string) : {
                [int, string, string, string, string, string, string, int]
            }
        """
        api_path = KrakenHarness._GET
        endpoint = 'OHLC'
        data = dict(zip(['pair', 'interval', 'since'], [pair, interval, since]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_orderbook(self, pair, count=""):
        """
        get order book for given asset pair
        Args :
            pair : (string) REQUIRED - asset pair to get market depth for
                    ex: XBTUSD
            count : (int) maximum number of asks/bids
                    100 - default
                    1 - 500  -  possible values
        Returns:
            pair nmame (string) : {
                asks : ask side array of array entries [<price>, <volume>, <timestamp>(int)]
                bids : bid side array of array entries[<price>, <volume>, <timestamp>(int)]
            }
        """
        api_path = KrakenHarness._GET
        endpoint = 'Depth'
        data = dict(zip(['pair', 'count'], [pair, count]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_recenttrades(self, pair, since=""):
        """
        gets the most recent trades of given pair since given timestamp
        returns the last 1000 trades by default
        Args:
            pair : (stirng) REQUIRED - asset pair to get trade data for
                    ex: XBTUSD
            since : (string) return trade data since given timestamp
        Returns:
            pair name (string) : [[<price>, <volume>, <time>(int), <buy/sell>, <market/limit>, <miscellaneous>]]
            last : (string) id to be used as since when polling for new trade data
        """
        api_path = KrakenHarness._GET
        endpoint = 'Trades'
        data = dict(zip(['pair', 'since'], [pair, since]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_recentspread(self, pair, since=""):
        """
        Args:
            pair : (string) REQUIRED - asset pair to get spread data for
            since : (string) return spread data since given id (optional.  inclusive)
        Returns:
            pair name (string) : [[<price>, <volume>, <time>(int), <buy/sell>, <market/limit>, <miscellaneous>]]
            last : (string) id to be used as since when polling for new trade data
        """
        api_path = KrakenHarness._GET
        endpoint = 'Spread'
        data = dict(zip(['pair', 'since'], [pair, since]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    ############# PRIVATE USER DATA FUNCTIONS ##############

    def get_accountbalance(self):
        """
        Retrieve all cash balances, net of pending withdrawals
        Returns:
            asset name (string) : (string) asset amount ,
            ...
            ...
        """
        api_path = KrakenHarness._POST
        endpoint = 'Balance'
        return self.process_response(self.make_request(api_path, endpoint))

    def get_tradebalance(self, asset=""):
        """
        Retrieve a summary of collateral balances, margin position valuations, equity and margin level.
        Args:
            asset : (string) base asset used to determine balance
                    ZUSD - default
        Returns:
            eb : equivalent balance (combined balance of all currencies)
            tb : trade balance (combined balance of all equity currencies)
            m : margin amount of open positions
            n : unrealized net profit/loss of open positions
            c : cost basis of open positions
            v : current floating valuation of open positions
            e : equity = trade balance + unrealized net profit/loss
            mf : free margin = equity - initial margin (maximum margin available to open new positions)
            ml : margin level = (equity / initial margin) * 100
        """
        api_path = KrakenHarness._POST
        endpoint = 'TradeBalance'
        data = dict(zip(['asset'], [asset]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_openorders(self, trades=False, userref=""):
        """
        Retrieve information about currently open orders.
        Args:
            trades: (bool) default = False
                whether or not to include trades relevant to position in output
            userref: (int) restrict results to given user reference id

        Returns:
            open : {
                ordertxid (string) : {
                    userref:(int)
                    status:
                    opentm:(int)
                    starttm:(int)
                    expiretm:(int)
                    descr: {
                        pair:
                        type:
                        ordertype:
                        price:
                        price2:
                        leverage:
                        order:
                        close:
                        }
                    vol:
                    vol_exec:
                    cost:
                    fee:
                    price:
                    stopprice:
                    limitprice:
                    misc:
                    oflags:
                    trades: [trade IDs (string)]
                }
        """
        api_path = KrakenHarness._POST
        endpoint = 'OpenOrders'
        data = dict(zip(['trades', 'userref'], [trades, userref]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_closedorders(self, trades=False, userref="", start="", end="", ofs="", closetime="both"):
        """
        Retrieve information about orders that have been closed (filled or cancelled). 50 results are
        returned at a time, the most recent by default.
        Note: If an order's tx ID is given for start or end time, the order's opening time (opentm) is used
        Args:
            trades: (bool) default = False
                Whether or not to include trades related to position in output
            userref: (int) Restricts results to given user reference id
            start: (int) Starting unix timestamp or order tx ID of results (exclusive)
            end: (int) Ending unix timestamp or order tx ID of results (inclusive)
            ofs: (int) Result offset for pagination
            closetime: (string) default = "both"
                "open"
                "close"
                "both"

        Returns:
            closed : {
                    ordertxid (string) : {
                        refid:
                        userref: (int)
                        status:
                        reason:
                        opentm: (int)
                        closetm: (int)
                        starttm: (int)
                        expiretm: (int)
                        descr: {
                            pair:
                            type:
                            ordertype:
                            price:
                            price2:
                            leverage:
                            order:
                            close:
                            }
                        vol:
                        vol_exec:
                        cost:
                        fee:
                        price:
                        stopprice:
                        limitprice:
                        misc:
                        oflags:
                        trades: [trade IDs (string)]
                    }
        """
        api_path = KrakenHarness._POST
        endpoint = 'ClosedOrders'
        data = dict(zip(['trades', 'userref', 'start', 'end', 'ofs', 'closetime'],
                        [trades, userref, start, end, ofs, closetime]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_orderinfo(self, txid, trades=False, userref=""):
        """
        Retrieve information about specific orders.
        Args:
            txid: (string) REQUIRED - Comma delimited list of transaction IDs to query info about (20 maximum)
            trades: (bool) default = False
                Whether or not to include trades related to position in output
            userref: (int) Restrict results to given user reference id

        Returns:
                ordertxid (string) : {
                    refid:
                    userref: (int)
                    status:
                    reason:
                    opentm: (int)
                    closetm: (int)
                    starttm: (int)
                    expiretm: (int)
                    descr: {
                        pair:
                        type:
                        ordertype:
                        price:
                        price2:
                        leverage:
                        order:
                        close:
                        }
                    vol:
                    vol_exec:
                    cost:
                    fee:
                    price:
                    stopprice:
                    limitprice:
                    misc:
                    oflags:
                    trades: [trade IDs (string)]
                }
        """
        api_path = KrakenHarness._POST
        endpoint = 'QueryOrders'
        data = dict(zip(['txid', 'trades', 'userref'], [txid, trades, userref]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_tradeshistory(self, type="", trades=False, start="", end="", ofs=""):
        """
        Retrieve information about trades/fills. 50 results are returned at a time, the most recent by default.
        Unless otherwise stated, costs, fees, prices, and volumes are specified with the precision for the asset pair
        (pair_decimals and lot_decimals), not the individual assets' precision (decimals).

        Args:
            type: (string) default -> "all"
                "all"
                "any position"
                "closed position"
                "closing position"
                "no position"
            trades: (bool) default -> False
                Whether or not to include trades related to position in output
            start: (int) Starting unix timestamp or trade tx ID of results (exclusive)
            end: (int) Ending unix timestamp or trade tx ID of results (inclusive)
            ofs:(int) Result offset for pagination

        Returns:
            trades:{
                ordertxid:
                posttxid:
                pair:
                time: (int)
                type:
                ordertype:
                price:
                cost:
                fee:
                vol:
                margin:
                misc:
        """
        api_path = KrakenHarness._POST
        endpoint = 'TradesHistory'
        data = dict(zip(['type', 'trades', 'start', 'end', 'ofs'], [type, trades, start, end, ofs]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_tradesinfo(self, txid, trades=False):
        """
        Retrieve information about specific trades/fills.
        Args:
            txid: (string) REQUIRED - Comma delimited list of transaction IDs to query info about (20 maximum)
            trades: (bool) default = False
                Whether or not to include trades related to position in output

        Returns:
            txid (string) :
                ordertxid :
                postxid :
                pair :
                time : (int)
                type :
                ordertype :
                price :
                cost :
                fee :
                vol :
                margin :
                misc :
        """
        api_path = KrakenHarness._POST
        endpoint = 'QueryTrades'
        data = dict(zip(['txid', 'trades'], [txid, trades]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_openpositions(self, txid="", docalcs=False, consolidation="market"):
        """
        Get information about open margin position
        Args:
            txid : (string) Comma delimited list of txids to limit output to
            docalcs : (bool) whether to include P&L calculations
            consolidation : (string) value = "market"
                            Consolidate positions by market/pair

        Returns:
         txid (string) :
                ordertxid :
                postxid :
                pair :
                time : (int)
                type :
                ordertype :
                cost :
                fee :
                vol :
                vol_close :
                margin :
                value :
                net :
                terms :
                rollovertm :
                misc :
                oflags :

        """
        api_path = KrakenHarness._POST
        endpoint = 'OpenPositions'
        data = dict(zip(['txid', 'docalcs', 'consoldiation'], [txid, docalcs, consolidation]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_ledgerspread(self, asset="", aclass="", type="all", start="", end="", ofs=""):
        """
        Retrieve information about ledger entries.
        50 results are returned at a time, the most recent by default
        Args:
            asset: (string) Comma delimited list of assets to restrict output to
            aclass: (string) asset class
            type: (string) default = "all"
                    Type of ledger to retrieve
                    "all"
                    "deposit"
                    "withdrawal"
                    "trade"
                    "margin"
            start: (int) Starting unix timestamp or ledger ID of results (exclusive)
            end: (int) Ending unix timestamp or ledger ID of results (inclusive)
            ofs: (int) result offset for pagination

        Returns:
            ledger : {
                txid (string) : {
                    refid :
                    time : (int)
                    type :
                    subtype :
                    aclass :
                    asset :
                    amount :
                    fee :
                    balance :
                }
            }

        """
        api_path = KrakenHarness._POST
        endpoint = 'Ledgers'
        data = dict(zip(['asset', 'aclass', 'type', 'start', 'end', 'ofs'], [asset, aclass, type, start, end, ofs]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_ledgerinfo(self, id="", trades=False):
        """
        Retrieve information about specific ledger entries
        Args:
            id: (string) comma delimited list of ledger IDs to query info about (20 max)
            trades: (bool) default = False
                    whether or not to include trades related to position in output

        Returns:
            txid (string) : {
                refid :
                time : (int)
                trype :
                subtype :
                aclass :
                asset :
                amount :
                fee :
                balance:

        """
        api_path = KrakenHarness._POST
        endpoint = 'QueryLedgers'
        data = dict(zip(['id', 'trades'], [id, trades]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_tradevolume(self, pair, fee_info=True):
        """
        get the trade volume of a given pair
        Note: If an asset pair is on a maker/taker fee schedule, the taker side is given in fees and maker
        side in fees_maker.
        For pairs not on maker/taker, they will only be given in fees
        Args:
            pair: (string) REQUIRED - asset pair to get data from
                    (I think this can also be a comma delimited list?? )
                    ex : "XETCXETH,XBTUSD"
            fee_info: (bool) whether or not to inlcude fee info in results

        Returns:
            currency :
            volume :
            fees : {
                pair name (string) : {
                    fee :
                    minfee :
                    maxfee :
                    nextfee : (can be null)
                    nextvolume : (can be null)
                    tiervolume :
                }
            }
            fees_maker : {
                pair name (string) : {
                    fee :
                    minfee :
                    maxfee :
                    nextfee : (can be null)
                    nextvolume : (can be null)
                    tiervolume :
                }
            }
        """
        api_path = KrakenHarness._POST
        endpoint = 'TradeVolume'
        data = dict(zip(['pair', 'fee-info'], [[pair, fee_info]]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def request_report(self, report, description, format="CSV", fields="all", starttm="", endtm=""):
        """
        Request an export of trades or ledgers
        Args:
            report: (string) REQUIRED - type of data to export :
                    "trades"
                    "ledgers"
            description: (string) REQUIRED - description for the export
            format: (string) file format for export :
                    "CSV" - default
                    "TSV"
            fields: (string) comma delimited list of fields to include
                    "all" - default
                    trades : "ordertxid, time, oredertype, price, cost, fee, vol, margin, misc, ledgers"
                    ledgers : "refid, time, aclass, asset, amount, fee, balance"
            starttm: (int) UNIX timestamp for report start time (default 1 year ago)
            endtm: (int) UNIX timestamp for report end time

        Returns:
            id:
        """
        api_path = KrakenHarness._POST
        endpoint = 'AddExport'
        data = dict(zip(['report', 'format', 'description', 'fields', 'starttm', 'endtm'],
                        [report, format, description, fields, starttm, endtm]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_reportstatus(self, report):
        """
        Get status of requested data exports
        Args:
            report: (string) REQUIRED - type of reports to inquire about
                    "trades"
                    "ledgers"

        Returns:
            [
                {
                    id :
                    descr  :
                    format :
                    report :
                    subtype :
                    status :
                    flags :
                    fields :
                    createdtm :
                    expiretm :
                    starttm :
                    cmpletedtm :
                    datastarttm :
                    dataendtm :
                    aclass :
                    asset :
                },
            ...
            ]
        """
        api_path = KrakenHarness._POST
        endpoint = 'ExportStatus'
        data = dict(zip(['report'], [report]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_report(self, id, filename):
        """
        retrieve a processed data export
        Args:
            id: (string) REQUIRED - report ID to retrieve
            filename : (stirng) REQUIRED - name of the report

        Returns from Kraken:
            report : Binary zip archive containing report

        Function returns:
            zip file object  - Library needed zipfile
        """
        api_path = KrakenHarness._POST
        endpoint = 'RetrieveExport'
        data = dict(zip(['id'], [id]))
        post_data = self.make_post_data(data)
        # does not process response because response structure is different in the docs for this
        result = self.make_request(api_path, endpoint, post_data=post_data)
        print(result)
        z = zipfile.ZipFile(result)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        z.write(dir_path + '/' + filename)
        return True

    def delete_report(self, id, type):
        """
        delete exported trades/ledgers report
        Args:
            id: (string) REQUIRED - ID of report to delete or cancel
            type: (string) REQUIRED - delete or cancel
                    "cancel" - can only be used for queued or processing reports
                    "delete" - can only be used for reports that have already been processesd

        Returns:
            delete : (bool)
        """
        api_path = KrakenHarness._POST
        endpoint = 'RemoveExport'
        data = dict(zip(['id', 'type'], [id, type]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    ############# PRIVATE USER FUNDING AND TRADING FUNCTIONS ##############

    def add_order(self, ordertype, type, pair, userref="", volume="",
                  price="", price2="", leverage="", oflags="", starttm="",
                  expiretm="", close_ordertype="", close_price="", close_price2="",
                  trading_agreement="", validate=False):
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
                    # will either add or subtract the amount to the last traded price,
                        depending on direction and order type used.
                    Relative prices can be suffixed with a % to signify the relative amount as a percentage.
            leverage: (string) amount of leverage desired
                    default = none
            oflags: (string) comma delimited list of order flags
                    "post" post-only order (available when ordertype = limit)
                    "fcib" prefer fee in base currency (default if selling)
                    "fciq" prefer fee in quote currency (default if buying, mutually exclusive with fcib)
                    "nompp" disable market price protection for market orders
            starttm: (string) scheduled start time of order can be specified as a specific time stamp or number of
                                seconds in future
                    "0" now (default)
                    "+<n>" schedule start time seconds from now
                    "<n>" = unix timestamp of start time
            expiretm: (string) order expiration time, follows same rules as starttm
                    "0" no expiration (default)
                    "+<n>" = expire seconds from now, minimum 5 seconds
                    "<n>" = unix timestamp of expiration time
            close_ordertype: (string) conditional close order type see:
                            https://support.kraken.com/hc/en-us/articles/360038640052-Conditional-Close
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
        api_path = KrakenHarness._POST
        endpoint = 'AddOrder'
        data = dict(zip(['userref', 'ordertype', 'type', 'volume', 'pair', 'pair',
                         'price', 'price2', 'leverage', 'oflags', 'starttm', 'expiretm',
                         'close[ordertype]', 'close[price]', 'close[price2]',
                         'trading_agreement', 'validate'],
                        [userref, ordertype, type, volume, pair, price, price2,
                         leverage, oflags, starttm, expiretm, close_ordertype,
                         close_price, close_price2, trading_agreement, validate]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def cancel_order(self, txid):
        """

        Args:
            txid: (string or integer) REQUIRED - Open order transaction ID (txid) or user reference (userref)

        Returns:
            count: number of orders canceled(?)
        """
        api_path = KrakenHarness._POST
        endpoint = 'CancelOrder'
        data = dict(zip(['txid'], [txid]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def cancle_allorders(self):
        """

        Returns:
            count: number of orders canceled(?)
        """
        api_path = KrakenHarness._POST
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
        api_path = KrakenHarness._POST
        endpoint = 'CancelAllOrdersAfter'
        data = dict(zip(['timeout'], [timeout]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

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
        api_path = KrakenHarness._POST
        endpoint = 'DepositMethods'
        data = dict(zip(['asset'], [asset]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_depositaddress(self, asset, method, new=True):
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
        api_path = KrakenHarness._POST
        endpoint = 'DepositAddresses'
        data = dict(zip(['asset', 'method', 'new'], [asset, method, new]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_depositstatus(self, asset, method=""):
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
        api_path = KrakenHarness._POST
        endpoint = 'DepositStatus'
        data = dict(zip(['asset', 'method'], [asset, method]))
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
        api_path = KrakenHarness._POST
        endpoint = 'WithdrawInfo'
        data = dict(zip(['asset', 'key', 'amount'], [asset, key, amount]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def withdraw_funds(self, asset, key, amount):
        """
        Retrieve fee information about potential withdrawals for a particular asset, key and amount.
        Args:
            asset: (string) REQUIRED - asset being withdrawn
            key: (string) REQUIRED - withdrawal key name, as set up on your account
            amount: (string) REQUIRED - amount to be withdrawn

        Returns:
            refid:
        """
        api_path = KrakenHarness._POST
        endpoint = 'Withdraw'
        data = dict(zip(['asset', 'key', 'amount'], [asset, key, amount]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def get_withdrawstatus(self, asset, method=""):
        """
        Retrieve fee information about potential withdrawals for a particular asset, key and amount.
        Args:
            asset: (string) REQUIRED - asset being withdrawn
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
        api_path = KrakenHarness._POST
        endpoint = 'WithdrawStatus'
        data = dict(zip(['asset', 'method'], [asset, method]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def cancel_withdraw(self, asset, refid):
        """
        Retrieve fee information about potential withdrawals for a particular asset, key and amount.
        Args:
            asset: (string) REQUIRED - asset being withdrawn
            refid: (string) REQUIRED - withdrawal reference ID

        Returns:
            result:
        """
        api_path = KrakenHarness._POST
        endpoint = 'WithdrawlCancel'
        data = dict(zip(['asset', 'refid'], [asset, refid]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))

    def request_wallet_transfer(self, asset, amount, frm="Spot Wallet", to="Futures Wallet"):
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
        api_path = KrakenHarness._POST
        endpoint = 'WalletTransfer'
        data = dict(zip(['asset', 'from', 'to', 'amount'], [asset, frm, to, amount]))
        post_data = self.make_post_data(data)
        return self.process_response(self.make_request(api_path, endpoint, post_data=post_data))
