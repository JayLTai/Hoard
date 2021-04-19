from web3 import Web3, middleware
from web3.gas_strategies.time_based import *
import json
import pdb

class Hoard:
    def __init__(self):
        self.wallets = {}

class Wallet:
    def __init__(self,name,address,prvkey):
        self.name = name
        self.address = address
        self.prvkey = prvkey

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


#connecting to the blockchain
#WebSocket connection can scale vertically on a single server, whereas REST, which is HTTP based, can scale horizontally.
web3 = _Ropsten_websocket
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
print("AmericanChinaman's transaction number is : {}".format(web3.eth.get_transaction_count(AmericanChinaman_address)))

#setting gas price strategy
web3.eth.setGasPriceStrategy(fast_gas_price_strategy)



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
        nonce = web3.eth.get_transaction_count(from_addr),
        gasPrice = web3.eth.gasPrice,
        # there must be an automated way to automatically set the gas price
        # based off of the gas strategy
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
    converts that returned HexBytes object into a string hex hash
    Args:
        signed_txn [obj] : a signed transaction obejct
    Returns:
        the transaction hash as a HexBytes object
    """
    return web3.eth.send_raw_transaction(signd_txn.rawTransaction).hex()

def wait_for_receipt(txn_hash, timeout=120, poll_latency=0.1):
    """
    waits for the traansaction specified by the given transaction hash to be 
    included in a block. Then returns the transaction receipt
    Args:
        txn_hash (str)      : string representing the transaction hash after its been
                             sent
        timeout (int)       : OPTIONAL a timeout for waiting for the receipt
        poll_latency (int)  : OPTIONAL latency at which to poll for receipt
    Returns:
        Attribute object which is the receipt of the transaction once added to a block
        EX:
            AttributeDict({
                'blockHash': '0x4e3a3754410177e6937ef1f84bba68ea139e8d1a2258c5f85db9f1cd715a1bdd',
                'blockNumber': 46147,
                'contractAddress': None,
                'cumulativeGasUsed': 21000,
                'from': '0xA1E4380A3B1f749673E270229993eE55F35663b4',
                'gasUsed': 21000,
                'logs': [],
                'logsBloom': '0x000000000000000000000000000000000000000000000000...0000',
                'status': 1,
                'to': '0x5DF9B87991262F6BA471F09758CDE1c0FC1De734',
                'transactionHash': '0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060',
                'transactionIndex': 0,
            })
    """
    return web3.eth.waitForTransactionReceipt(txn_hash,timeout,poll_latency)

def get_tnx_block(block_id, full_transactions=False):
    """
    gets the block information of a given block, identified with its block hash
    Args:
        block_id (int) : an int representing the ID of the block
    Returns:
        Dicionary object that represents the depicts all that goes into a 
        transaction boss
        EX:
            AttributeDict({
                'difficulty': 49824742724615,
                'extraData': '0xe4b883e5bda9e7a59ee4bb99e9b1bc',
                'gasLimit': 4712388,
                'gasUsed': 21000,
                'hash': '0xc0f4906fea23cf6f3cce98cb44e8e1449e455b28d684dfa9ff65426495584de6',
                'logsBloom': '0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
                'miner': '0x61c808d82a3ac53231750dadc13c777b59310bd9',
                'nonce': '0x3b05c6d5524209f1',
                'number': 2000000,
                'parentHash': '0x57ebf07eb9ed1137d41447020a25e51d30a0c272b5896571499c82c33ecb7288',
                'receiptRoot': '0x84aea4a7aad5c5899bd5cfc7f309cc379009d30179316a2a7baa4a2ea4a438ac',
                'sha3Uncles': '0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347',
                'size': 650,
                'stateRoot': '0x96dbad955b166f5119793815c36f11ffa909859bbfeb64b735cca37cbf10bef1',
                'timestamp': 1470173578,
                'totalDifficulty': 44010101827705409388,
                'transactions': ['0xc55e2b90168af6972193c1f86fa4d7d7b31a29c156665d15b9cd48618b5177ef'],
                'transactionsRoot': '0xb31f174d27b99cdae8e746bd138a01ce60d8dd7b224f7c60845914def05ecc58',
                'uncles': [],
            })
    
    """
    return web3.eth.get_block(block_id, full_transactions)

def trade(send_Wallet, recv_Wallet, amount):
    send_balance = web3.eth.get_balance(send_Wallet.address)
    recv_balance = web3.eth.get_balance(recv_Wallet.address)
    #Transaction sequence moving from send_Wallet to rcv_Wallet
    print('{s:{c}^{n}}'.format(s=' creating transaction data ', n=80, c='*'))
    txn = mk_simple_transaction(send_Wallet.address,recv_Wallet.address,amount)
    print(txn)
    print('{s:{c}^{n}}'.format(s=' signing transaction ', n=80, c='*'))
    signed_txn = sign_transaction(txn, send_Wallet.prvkey)
    print("signed transaction hash = {}".format(signed_txn))
    print('{s:{c}^{n}}'.format(s=' sending transaction ', n=80, c='*'))
    txn_hash = send_transaction(signed_txn)
    print("transaction hash = {}".format(txn_hash))
    print('{s:{c}^{n}}'.format(s=' getting transaction receipt ', n=80, c='*'))
    receipt = wait_for_receipt(txn_hash)
    # pdb.set_trace()
    print(receipt)
    print('{s:{c}^{n}}'.format(s=' getting block transaction was a part of ', n=80, c='*'))\
    #realistically this part of confirming the status of the block & transaction (mined or not)
    #might be able to be checked using the reciept? Not sure though
    #Answer : Looks like once we get a receipt from the transaction, the transaction will have
    # been completed and added to the ledger (aka block is mined i believe)
    block = get_tnx_block(receipt.blockNumber)
    # pdb.set_trace()
    print(block)
    print("**********************************************************************************")
    print("{name}'s OLD account balance in wei is : {amount}".format(name=send_Wallet.name,amount=send_balance))
    send_balance = web3.eth.get_balance(send_Wallet.address)
    print("{name}'s NEW account balance in wei is : {amount}".format(name=send_Wallet.name,amount=send_balance))
    print("                   ----------------------------------------                       ")
    print("{name}'s OLD account balance in wei is : {amount}".format(name=recv_Wallet.name,amount=recv_balance))
    recv_balance = web3.eth.get_balance(recv_Wallet.address)
    print("{name}'s NEW account balance in wei is : {amount}".format(name=recv_Wallet.name,amount=recv_balance))
    #this sequence seems to be flakey occasionally. no idea why. probabaly a timing thing that might 
    #might go away with differnet impelmentation



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