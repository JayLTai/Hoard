from web3 import Web3
import json


#Infura HTTP MainNet:
_Mainnet_http = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/cfafd2526e9e45c8947689373933aa87'))
#Infura websocket MainNet:
_Mainenet_websocket = Web3(Web3.WebsocketProvider('wss://mainnet.infura.io/ws/v3/cfafd2526e9e45c8947689373933aa87'))

#Infura HTTP Ropsten:
_Ropsten_http = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/cfafd2526e9e45c8947689373933aa87'))
#Infura websocket Ropsten:
_Ropsten_websocket = Web3(Web3.WebsocketProvider('wss://ropsten.infura.io/ws/v3/cfafd2526e9e45c8947689373933aa87'))

#sounds like we need to set a gas price strategy at some point

JT_Main_address = '0xb5ED1E2eeB6078529ED32Ce228BFe3aE132d3aAB'
AmericanChinaman_address = '0xFEC7506eBfC2bae176Af49f946653efBE16eeaF3'
AmericanChinaman_prvkey = '7a6dac22e8a127cc49f25efcfeb68521817fe7c4bc538fd287f4d16809ad427e'
BusinessChinaman_address = '0xa2841602F157F4F5195dA04EC6EF5e38C5E355c2'
BusinessChinaman_prvkey = '9d0752977e272a0d5e012e113d48176a3592b944de505b8ca8aaf81bc7b302d3'



web3 = _Ropsten_http

print("Connection to the blockchain is : {}".format(web3.isConnected()))

JT_Main_balance = web3.eth.get_balance(JT_Main_address)
AmericanChinaman_balance = web3.eth.get_balance(AmericanChinaman_address)
BusinessChinaman_balance = web3.eth.get_balance(BusinessChinaman_address)
print("JT's Main account balance in wei is : {}".format(JT_Main_balance))
print("AmericanChinaman's account balance in wei is : {}".format(AmericanChinaman_balance))
print("BusinessChinaman's account balance in wei is : {}".format(BusinessChinaman_balance))
print("JT's Main account balance in ether is : {}".format(web3.fromWei(JT_Main_balance, 'ether')))
print("AmericanChinaman's account balance in ether is : {}".format(web3.fromWei(AmericanChinaman_balance, 'ether')))
print("BusinessChinaman's account balance in ether is : {}".format(web3.fromWei(BusinessChinaman_balance, 'ether')))

def mk_simple_transaction(from_addr, to_addr, send_value):
    """
    creates a simple transaction that sends a certain amount of wei from one 
    address to another
    Args:
        from_addr (str) : string denoting the address to send from
        to_addr (str)   : string denoting the address to send to
        send_value (int): the number value in Wei to be sent 
    Returns:
        a dictionary object representing the created simple transaction
    """
    transaction = dict(
        nonce = web3.eth.getTransactionCount(from_addr),
        gasPrice = web3.eth.gasPrice,
        gas = 100000,
        to = to_addr,
        value = web3.toWei(send_value, 'wei')
    )
    return transaction

def sign_transaction(transaction, prvkey):
    """
    signs a given transaction so it can be sent.
    Args:
        transaction (dict) : a dictionary object representing a given transaction to be made
        prvkey (str)       : the private key of the account making the transaction
    Returns:
        a transaction object that has been signed 
    """
    return web3.eth.account.sign_transaction(transaction, prvkey)

def send_transaction(signd_txn):
    """
    sends a signed and serialized transaction. 
    Args:
        signed_txn [obj] : a signed transaction obejct
    Returns:
        the transaction hash as a HexBytes object
    """
    return web3.eth.send_raw_transaction(signd_txn.rawTransaction)

txn = mk_simple_transaction(AmericanChinaman_address,BusinessChinaman_address,1)
signed_txn = sign_transaction(txn, AmericanChinaman_prvkey)
print(send_transaction(signed_txn))