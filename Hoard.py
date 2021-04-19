from  Eth_tools import *
# import Tree
from Exchange import *
import json

PublicKeys = {
    'kraken' : "/cMR5bE3cclVQhuHtpP4ZY1fzcCtwHdo/14v7TJ3rTHF8L/L1UxkxDPx"
}

PrivateKeys = {
    'kraken' : "+TQJz3j7n9nAlPAQXJlMoRnl0QWuzJ8fO4pE5BC4eogCFS157mAOEUTxBhFRBGk5e6VVXt4Djb9zO7VaztHVDw=="
}

Kraken = Kraken_Harness(apiPublicKey = PublicKeys['kraken'], apiPrivateKey = PrivateKeys['kraken'])
print(Kraken.get_servertime())
print(Kraken.get_systemstatus())