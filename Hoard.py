from web3 import Web3

#Infura HTTP MainNet:
_Mainnet_http = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/cfafd2526e9e45c8947689373933aa87'))
#Infura websocket MainNet:
_Mainenet_websocket = Web3(Web3.WebsocketProvider('wss://mainnet.infura.io/ws/v3/cfafd2526e9e45c8947689373933aa87'))

#Infura HTTP Ropsten:
_Ropsten_http = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/cfafd2526e9e45c8947689373933aa87'))
#Infura websocket Ropsten:
_Ropsten_websocket = Web3(Web3.WebsocketProvider('wss://ropsten.infura.io/ws/v3/cfafd2526e9e45c8947689373933aa87'))

JT_Main_address = '0xb5ED1E2eeB6078529ED32Ce228BFe3aE132d3aAB'
AmericanChinaman_address = '0xFEC7506eBfC2bae176Af49f946653efBE16eeaF3'

web3 = _Ropsten_http

print("Connection to the blockchain is : {}".format(web3.isConnected()))

JT_Main_balance = web3.eth.get_balance(JT_Main_address)
AmericanChinaman_balance = web3.eth.get_balance(AmericanChinaman_address)
print("JT's Main account balance in wei is : {}".format(JT_Main_balance))
print("JT's Main account balance in wei is : {}".format(AmericanChinaman_balance))
print("JT's Main account balance in ether is : {}".format(web3.fromWei(JT_Main_balance, 'ether')))
print("JT's Main account balance in ether is : {}".format(web3.fromWei(AmericanChinaman_balance, 'ether')))