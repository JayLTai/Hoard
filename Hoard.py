from  Eth_tools import *
# import Tree
from Kraken_Harness import *
import json

PublicKeys = {
    'kraken' : "KPLlDob0WfygtiDknD0BG6TkuWDuEGC+zaNoYXry9nK4E0ayWmgubX1D"
}

PrivateKeys = {
    'kraken' : "j6tvLYKj7Pz5z6AhsG7Rd0sgN1+nyptOPt3g7A1X8MQYApfQh1AyM7VsTrVT6S4zqXEd1udU02NQNTTd0HFdoQ=="
}

Kraken = Kraken_Harness(apiPublicKey = PublicKeys['kraken'], apiPrivateKey = PrivateKeys['kraken'])
print(Kraken.get_servertime())
print(Kraken.get_systemstatus())
# print(Kraken.get_assetinfo())
print("_____________________________________________________")
print(Kraken.get_assetinfo(asset = 'XETH'))
# print("_____________________________________________________")
print(Kraken.get_assetinfo(aclass = 'currency', asset = 'DAI'))
print("_____________________________________________________")
print("____________________Asset Pairs______________________")
print("_____________________________________________________")
print(Kraken.get_assetpairs(info = "info", pair = 'ETHUSD'))
print("_____________________________________________________")
print(Kraken.get_assetpairs(info = "info", pair = 'ETHBTC'))
print("_____________________________________________________")
print("____________________Ticker Info______________________")
print("_____________________________________________________")
print(Kraken.get_tickerinfo(pair = 'ETHUSD'))
print("_____________________________________________________")
print("______________________OHLC Info______________________")
print("_____________________________________________________")
print(Kraken.get_ohlc(pair = 'ETHUSD', interval = '1'))
print("_____________________________________________________")
print("______________________Order Book_____________________")
print("_____________________________________________________")
print(Kraken.get_orderbook(pair = 'ETHUSD', count = '1'))
print("_____________________________________________________")
print("____________________Recent Trades____________________")
print("_____________________________________________________")
print(Kraken.get_recenttrades(pair = 'ETHUSD'))
print("_____________________________________________________")
print("_________________Recent Spread Data__________________")
print("_____________________________________________________")
print(Kraken.get_recentspread(pair = 'ETHUSD'))
print('{s:{c}^{n}}'.format(s='      +      ', n=100, c='+'))
print('{s:{c}^{n}}'.format(s='      +      ', n=100, c='+'))
print('{s:{c}^{n}}'.format(s='      PRIVATE STUFF      ', n=100, c='+'))
print('{s:{c}^{n}}'.format(s='      +      ', n=100, c='+'))
print('{s:{c}^{n}}'.format(s='      +      ', n=100, c='+'))
# print(Kraken.get_tradebalance(aclass = 'currency', asset ='XETH'))
print(Kraken.get_accountbalance())