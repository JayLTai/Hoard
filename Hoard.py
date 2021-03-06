import json
import os

class Hoard:
    """
    Hoard will be the overarching class object that will manage all the trading 
    and financial information. 
    Args:
        Eth       : (Eth Object) an Eth object, representing the connection to 
                    the ethereum blockchain
        wallets   : (dict) a dictionary of Wallet objects 
                    {name (string) : (address,private key)}
                    This needs to be turned into a database that has:
                        wallet amount
                        wallet transaction log
                        wallet nonce
                    maybe create an object that gets populated by the databse call
        Kraken     : (Kraken_Harness Object) a Kraken_Harness object representing 
                     the connection to a Kraken Exchange API
        Trading information : tbd
        other stuff tbd
    Attributes:
        Eth       : (Eth Object) an Eth object, representing the connection to 
                    the ethereum blockchain
        wallets   : (dict) a dictionary of Wallet objects 
                    {name (string) : (address,private key)}

    """
    def __init__(self, Eth_Harness = None, Wallets = {}, Kraken = None):
        self.Eth_Harness = Eth_Harness
        self.Wallets = Wallets
        self.Kraken_Harness = Kraken