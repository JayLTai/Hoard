from Eth_tools import *
from Kraken_Harness import *
from Hoard import *
import json
import os

with open('keys.json') as data_file:
    data = json.load(data_file)

infura_http = data['Infura']['Ropsten']['HTTP']
Eth_Ropsten = HTTPEth(infura_http)

w = data['Wallets']
Wallets = {}
for k,p in w.items():
    Wallets[k]=(Wallet(name = k))
    for param,val in p.items():
        Wallets[k].json_import(param,val)

kAPI = data['Kraken']['TEST']['APIKey']
kPrv = data['Kraken']['TEST']['PrivateKey']
Kraken = Kraken_Harness(api_publickey = kAPI, api_privatekey = kPrv)


Hoard = Hoard(Eth_Harness = Eth_Ropsten, wallets = Wallets, Kraken = Kraken)

def test_web3():
    web3 = Hoard.Eth_Harness.web3

    JT_Main_address = Hoard.wallets['JT'].address
    AmericanChinaman_address = Hoard.wallets['AmericanChinaman'].address
    BusinessChinaman_address = Hoard.wallets['BusinessChinaman'].address

    # connecting to the blockchain
    # WebSocket connection can scale vertically on a single server, whereas REST, which is HTTP based, can scale horizontally.
    print("!!!!!!!!!!  Connection to the blockchain is : {}  !!!!!!!!!".format(web3.isConnected()))
    print("**********************************************************************************")
    JT_Main_balance = web3.eth.get_balance(JT_Main_address)
    AmericanChinaman_balance = web3.eth.get_balance(AmericanChinaman_address)
    BusinessChinaman_balance = web3.eth.get_balance(BusinessChinaman_address)
    print("JT's Main account balance in wei is : {}".format(JT_Main_balance))
    print("AmericanChinaman's account balance in wei is : {}".format(AmericanChinaman_balance))
    print("BusinessChinaman's account balance in wei is : {}".format(BusinessChinaman_balance))
    print("**********************************************************************************")
    print("JT's Main account balance in ether is : {}".format(web3.fromWei(JT_Main_balance, 'ether')))
    print("AmericanChinaman's account balance in ether is : {}".format(web3.fromWei(AmericanChinaman_balance, 'ether')))
    print("BusinessChinaman's account balance in ether is : {}".format(web3.fromWei(BusinessChinaman_balance, 'ether')))
    print("**********************************************************************************")
    print("AmericanChinaman's transaction number is : {}".format(
        web3.eth.get_transaction_count(AmericanChinaman_address)))

    # setting gas price strategy
    web3.eth.setGasPriceStrategy(fast_gas_price_strategy)

    # AmericanChinaman = Wallet('AmericanChinaman',AmericanChinaman_address,AmericanChinaman_prvkey)
    # BusinessChinaman = Wallet('BusinessChinaman',BusinessChinaman_address,BusinessChinaman_prvkey)

    # AC_before_1 = web3.eth.get_balance(AmericanChinaman.address)
    # BC_before_1 = web3.eth.get_balance(BusinessChinaman.address)
    # trade(AmericanChinaman, BusinessChinaman, 10000000)
    # AC_after_1 = web3.eth.get_balance(AmericanChinaman.address)
    # BC_after_1 = web3.eth.get_balance(BusinessChinaman.address)
    # trade(BusinessChinaman, AmericanChinaman, 10000000)
    # AC_after_2 = web3.eth.get_balance(AmericanChinaman.address)
    # BC_after_2 = web3.eth.get_balance(BusinessChinaman.address)

    # print("{name}'s  account balance went from  : {a1} ----> {a2} ----> {a3}".format(name=AmericanChinaman.name,a1=AC_before_1, a2=AC_after_1, a3=AC_after_2))
    # print("{name}'s  account balance went from  : {a1} ----> {a2} ----> {a3}".format(name=BusinessChinaman.name,a1=BC_before_1, a2=BC_after_1, a3=BC_after_2))

def test_kraken_publics():
    Kraken = Hoard.Kraken_Harness
    print(Kraken.get_servertime())
    print(Kraken.get_systemstatus())
    # print(Kraken.get_assetinfo())
    print("_____________________________________________________")
    print(Kraken.get_assetinfo(asset='ETH'))
    # print("_____________________________________________________")
    print(Kraken.get_assetinfo(aclass='currency', asset='DAI'))
    print("_____________________________________________________")
    print("____________________Asset Pairs______________________")
    print("_____________________________________________________")
    print(Kraken.get_assetpairs(info="info", pair='ETHUSD'))
    print("_____________________________________________________")
    print(Kraken.get_assetpairs(info="info", pair='ETHBTC'))
    print("_____________________________________________________")
    print("____________________Ticker Info______________________")
    print("_____________________________________________________")
    print(Kraken.get_tickerinfo(pair='ETHUSD'))
    print("_____________________________________________________")
    print("______________________OHLC Info______________________")
    print("_____________________________________________________")
    print(Kraken.get_ohlc(pair='ETHUSD', interval='1'))
    print("_____________________________________________________")
    print("______________________Order Book_____________________")
    print("_____________________________________________________")
    print(Kraken.get_orderbook(pair='ETHUSD', count='1'))
    print("_____________________________________________________")
    print("____________________Recent Trades____________________")
    print("_____________________________________________________")
    print(Kraken.get_recenttrades(pair='ETHUSD'))
    print("_____________________________________________________")
    print("_________________Recent Spread Data__________________")
    print("_____________________________________________________")
    print(Kraken.get_recentspread(pair='ETHUSD'))

def test_kraken_userdata():
    Kraken = Hoard.Kraken_Harness
    # print(Kraken.get_tradebalance())
    print("_____________________________________________________")
    print("_________________  Account Balance __________________")
    print("_____________________________________________________")
    print(Kraken.get_accountbalance())

def test_kraken_trading():
    Kraken = Hoard.Kraken_Harness
    print("_____________________________________________________")
    print("_________________     Add Order    __________________")
    print("_____________________________________________________")
    print(Kraken.add_order(ordertype="limit", type="buy", volume="1.25",
                           pair="XETHZUSD", price="275", validate=True))

def test_kraken_funding():
    Kraken = Hoard.Kraken_Harness
    print("_____________________________________________________")
    print("_________________  deposit methods  _________________")
    print("_____________________________________________________")
    print(Kraken.get_depositmethods(asset="ETH"))
    print("_____________________________________________________")
    print("_________________  deposit status  -_________________")
    print("_____________________________________________________")
    print(Kraken.get_depositstatus(asset="ETH"))
    print("_____________________________________________________")
    print("_________________  withdrawal info  _________________")
    print("_____________________________________________________")
    print(Kraken.get_withdrawalinfo(asset="ETH", key="FundsKey", amount="0"))
    print("!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!ERROR!!!!")
    print("_____________________________________________________")
    print("_____________  get withdrawal status  _______________")
    print("_____________________________________________________")
    print(Kraken.get_withdrawstatus(asset="ETH"))

if __name__ ==  "__main__" :
    test_kraken_publics()

