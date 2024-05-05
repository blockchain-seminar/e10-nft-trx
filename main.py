from web3 import Web3

from config import infura_api_key
from data_processing import fetch_blocks
from db_connections import get_latest_blocks

def initialize():
    # TODO
    pass

def main():
    url = f'https://mainnet.infura.io/v3/{infura_api_key}'
    #url = 'http://127.0.0.1:8547'
    web3 = Web3(Web3.HTTPProvider(url))

    block_latest, block_lowest_fetched, block_highest_fetched = get_latest_blocks(web3)
    
    n=1000
    if block_lowest_fetched is None or block_highest_fetched is None:
      fetch_blocks(block_latest-n, block_latest, web3)
    else:
      fetch_blocks(block_lowest_fetched-n, block_lowest_fetched-1, web3)   

if __name__ == "__main__":
    initialize()  
    main()       
