from Eth_tools import *
from Kraken_Harness import *
from Hoard import *
import json

with open('keys.json') as data_file:
    data = json.load(data_file)

infura_http = data['Infura']['Ropsten']['HTTP']
Eth_Ropsten = HTTPEth(infura_http)

w = data['Wallets']
Wallets = {}
for k, p in w.items():
    Wallets[k] = (Wallet(name=k))
    for param, val in p.items():
        Wallets[k].json_import(param, val)

kAPI = data['Kraken']['TEST']['APIKey']
kPrv = data['Kraken']['TEST']['PrivateKey']
Kraken = KrakenHarness(api_publickey=kAPI, api_privatekey=kPrv)

Hoard = Hoard(Eth_Harness=Eth_Ropsten, Wallets=Wallets, Kraken=Kraken)


def test_web3():
    web3 = Hoard.Eth_Harness.web3
    JT_Main_address = Hoard.Wallets['JT'].address
    AmericanChinaman_address = Hoard.Wallets['AmericanChinaman'].address
    BusinessChinaman_address = Hoard.Wallets['BusinessChinaman'].address
    print("\n_____________________________________________________")
    print("________________  BASIC WEB3 TEST  __________________")
    print("_____________________________________________________")
    # connecting to the blockchain
    # WebSocket connection can scale vertically on a single server,
    # whereas REST, which is HTTP based, can scale horizontally.
    print("!!!!!!!!!!  Connection to the blockchain is : {}  !!!!!!!!!".format(web3.isConnected()))
    print("**********************************************************************************")
    JT_Main_balance = web3.eth.get_balance(JT_Main_address)
    AmericanChinaman_balance = web3.eth.get_balance(AmericanChinaman_address)
    BusinessChinaman_balance = web3.eth.get_balance(BusinessChinaman_address)
    print("JT's Main account balance in wei is              : {}".format(JT_Main_balance))
    print("AmericanChinaman's account balance in wei is     : {}".format(AmericanChinaman_balance))
    print("BusinessChinaman's account balance in wei is     : {}".format(BusinessChinaman_balance))
    print("**********************************************************************************")
    print("JT's Main account balance in ether is            : {}".format(web3.fromWei(JT_Main_balance, 'ether')))
    print(
        "AmericanChinaman's account balance in ether is   : {}".format(web3.fromWei(AmericanChinaman_balance, 'ether')))
    print(
        "BusinessChinaman's account balance in ether is   : {}".format(web3.fromWei(BusinessChinaman_balance, 'ether')))
    print("**********************************************************************************")
    print("AmericanChinaman's transaction number is         : {}".format(
        web3.eth.get_transaction_count(AmericanChinaman_address)))
    print("BusinessChinaman's transaction number is         : {}".format(
        web3.eth.get_transaction_count(BusinessChinaman_address)))


def test_web3_transfer():
    web3 = Hoard.Eth_Harness.web3
    Eth_Harness = Hoard.Eth_Harness
    AmericanChinaman = Hoard.Wallets['AmericanChinaman']
    BusinessChinaman = Hoard.Wallets['BusinessChinaman']
    AmericanChinaman_address = AmericanChinaman.address
    BusinessChinaman_address = BusinessChinaman.address
    # setting gas price strategy
    web3.eth.setGasPriceStrategy(fast_gas_price_strategy)
    print("\n_____________________________________________________")
    print("______________  WEB3 ETH TRANSACTION  _______________")
    print("_____________________________________________________")
    AC_before_1 = web3.eth.get_balance(AmericanChinaman_address)
    BC_before_1 = web3.eth.get_balance(BusinessChinaman_address)
    print("\n FIRST  TRADE -- AC -> bc")
    Eth_Harness.trade(AmericanChinaman, BusinessChinaman, 10000000)
    AC_after_1 = web3.eth.get_balance(AmericanChinaman_address)
    BC_after_1 = web3.eth.get_balance(BusinessChinaman_address)
    print("\n SECOND TRADE -- BC -> AC")
    Eth_Harness.trade(BusinessChinaman, AmericanChinaman, 10000000)
    AC_after_2 = web3.eth.get_balance(AmericanChinaman_address)
    BC_after_2 = web3.eth.get_balance(BusinessChinaman_address)
    print("\n{name}'s  account balance went from  : \n{a1} ----> {a2} ----> {a3}".format(name=AmericanChinaman.name,
                                                                                     a1=AC_before_1, a2=AC_after_1,
                                                                                     a3=AC_after_2))
    print("{name}'s  account balance went from  : \n{a1} ----> {a2} ----> {a3}".format(name=BusinessChinaman.name,
                                                                                     a1=BC_before_1, a2=BC_after_1,
                                                                                     a3=BC_after_2))


def test_kraken_publics():
    Kraken = Hoard.Kraken_Harness
    print("\n_____________________________________________________")
    print("_________________  PUBLICS KRAKEN  __________________")
    print("_____________________________________________________")
    print("server time info              :   {a}".format(a=repr(Kraken.get_servertime())))
    print("system status info            :   {a}".format(a=repr(Kraken.get_systemstatus())))
    print("asset info for ETH & BTC      :   {a}".format(a=repr(Kraken.get_assetinfo(asset="XBT,ETH"))))
    print("asset info for DAI            :   {a}".format(a=repr(Kraken.get_assetinfo(asset='DAI'))))
    print("asset pair info               :   {a}".format(a=repr(Kraken.get_assetpairs(pair='ETHBTC'))))
    print("ticker info                   :   {a}".format(a=repr(Kraken.get_tickerinfo(pair='ETHUSD'))))
    print("OHLC data for ETHUSD          :   {a}".format(a=repr(Kraken.get_ohlc(pair='ETHUSD', interval='1'))))
    print("order book for ETHUSD         :   {a}".format(a=repr(Kraken.get_orderbook(pair='ETHUSD', count='1'))))
    print("recent trades for ETHUSD      :   {a}".format(a=repr(Kraken.get_recenttrades(pair='ETHUSD'))))
    print("recent spread data for ETHUSD :   {a}".format(a=repr(Kraken.get_recentspread(pair='ETHUSD'))))


def test_kraken_userdata():
    Kraken = Hoard.Kraken_Harness
    print("\n_____________________________________________________")
    print("___________  PRIVATES KRAKEN USER DATA  _____________")
    print("_____________________________________________________")
    print("kraken account balance        :   {a}".format(a=repr(Kraken.get_accountbalance())))
    # THIS ONE IS AN INTERNAL ERROR????????
    print("GET_TRADEBALANCE SKIPPED")
    # print("account trade balance         :   {a}".format(a = repr(Kraken.get_tradebalance(asset = "ZUSD"))))
    print("account open orders           :   {a}".format(a=repr(Kraken.get_openorders())))
    print("account closed orders         :   {a}".format(a=repr(Kraken.get_closedorders())))
    # get_orderinfo
    print(" GET_ORDERINFO SKIPPED")
    print("account trade history         :   {a}".format(a=repr(Kraken.get_tradeshistory())))
    # print("specific trade info           :   {a}".format(a = repr(Kraken.get_tradesinfo(TXID = ""))))
    print("get open positions            :   {a}".format(a=repr(Kraken.get_openpositions())))
    print("get ledger info               :   {a}".format(a=repr(Kraken.get_ledgerspread())))
    # get_ledgerinfo
    print("GET_LEDGERINFO SKIPPED")
    print("GET_TRADEVOLUME SKIPPED")
    # WTF INVALID ASSET PAIR????
    # print("trade volume of XBTUSD        :   {a}".format(a = repr(Kraken.get_tradevolume(pair = "XBTUSD"))))
    report = Kraken.request_report(report="trades", description="test_report")
    print("report of trades for ETHUSD   :   {a}".format(a=repr(report)))
    report_status = Kraken.get_reportstatus(report="trades")
    print("status of reports on account  :   {a}".format(a=repr(report_status)))
    report_id = report_status[0].get('id')
    while report_status[0].get('status') != "Processed":
        report_status = Kraken.get_reportstatus(report="trades")
    # probably gonna need to re check this function once requests is properly implemented
    print("GET_REPORT SKILLED")
    # report_zip = Kraken.get_report(id = report_id, filename = "test_report")
    # print("zip file of report            :   {a}".format(a = repr(report_zip)))
    print("delete test report            :   {a}".format(a=repr(Kraken.delete_report(id=report_id, type="delete"))))


def test_kraken_trading():
    print("\n_____________________________________________________")
    print("______________  KRAKEN TRADING CALLS  _______________")
    print("_____________________________________________________")
    Kraken = Hoard.Kraken_Harness
    print("ADD_ORDER SKIPPED")
    # test_validate_order = Kraken.add_order(ordertype="limit", type="buy", volume="1.25",
    #                        pair="XETHZUSD", price="275", validate=True)
    # print("add kraken order              :   {a}".format(a = repr(test_validate_order)))


def test_kraken_funding():
    print("\n_____________________________________________________")
    print("______________  KRAKEN FUNDING CALLS  _______________")
    print("_____________________________________________________")
    Kraken = Hoard.Kraken_Harness
    print("kraken account deposit methods:   {a}".format(a=repr(Kraken.get_depositmethods(asset="ETH"))))
    print("account deposit status        :    {a}".format(a=repr(Kraken.get_depositstatus(asset="ETH"))))
    print("GET_WITHDRAWALINFO SKIPPED")
    # print("account withdrawal info       :    {a}".format(a = repr(Kraken.get_withdrawalinfo(asset="ETH",
    #                                                                                          key="FundsKey",
    #                                                                                          amount="0"))))
    print("get withdrawal status        :     {a}".format(a=repr(Kraken.get_withdrawstatus(asset="ETH"))))


def main():
    # test_web3()
    # test_web3_transfer()
    test_kraken_publics()
    test_kraken_userdata()
    test_kraken_funding()
    test_kraken_trading()


if __name__ == "__main__":
    main()
