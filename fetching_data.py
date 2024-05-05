from web3 import Web3
from db_connections import get_fetched_blocks

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8547"))

def fetchLatestBlockData(web3):
    """ 
    We retrieve and print the latest block number on the Ethereum blockchain, as well as the minimum and maximum block numbers that we already fetched from the database:
        block_latest holds the number of the most recent block.
        block_lowest_fetched retrieves the smallest block number from the already fetched blocks using the get_fetched_blocks("min") function.
        block_highest_fetched retrieves the largest block number from the already fetched blocks using the get_fetched_blocks("max") function.
        Prints each of these values to provide a current snapshot of block synchronization status with the blockchain.
    """
    block_latest = web3.eth.block_number
    block_lowest_fetched = get_fetched_blocks("min")
    block_highest_fetched = get_fetched_blocks("max")

    print('block_latest ->', block_latest)
    print('block_lowest_fetched ->', block_lowest_fetched)
    print('block_highest_fetched ->', block_highest_fetched)
    
    return block_latest, block_lowest_fetched, block_highest_fetched

