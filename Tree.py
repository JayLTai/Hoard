from web3 import Web3, middleware
from websocket import create_connection
import sys
import signal
import json
import pdb
import requests


class Seed:
    """
    seed value is how much money in dollars it is worth
        i eventually want seed value to be a value exchange between cryptos (tuple)
    currency is the currency we are trying to trade it into

    """
    def __init__(self, price, currency):
        self.value = value
        self.currency = currency

class Root():
    """
    root price is the crypto value 
    value is how many dollars the root is currently worth
    cost is how many 
    """
    def __init__(self):
        self.value 
        self.price
        self.cost
        self.currency 
        


class Tree:
    """
    trees have a certain number of roots
    trees have a certain number of seeds
    when a root cuts a seed it produces a fruit 
    """
    def __init__(self):
        self.roots
        self.seeds
        self.fruits