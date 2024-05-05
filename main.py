import os
import time
import datetime
import pandas as pd
import requests
from requests.exceptions import HTTPError
from web3 import Web3
from pathlib import Path
import sqlite3 as sql
from tqdm import tqdm
import functools

import init
from data_processing import fetch_blocks
from fetching_data import fetchLatestBlockData
from transaction_processing import process_transaction

# Setup
etherscan_api_key = init.get_etherscan_api_key()
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8547"))

# Main operation flow
block_latest, block_lowest_fetched, block_highest_fetched = fetchLatestBlockData(web3)

# Event signature hashes for ERC-721 and ERC-1155 Transfer events
erc721_transfer = Web3.keccak(text='Transfer(address,address,uint256)').hex()
erc1155_transfer_single = Web3.keccak(text='TransferSingle(address,address,address,uint256,uint256)').hex()
erc1155_transfer_batch = Web3.keccak(text='TransferBatch(address,address,address,uint256[],uint256[])').hex()

fetchLatestBlockData(web3)

""" 
The range of blocks to fetch is determined based on the data already fetched and stored in the database:
If no blocks have been fetched previously (i.e., block_lowest_fetched or block_highest_fetched is None), it fetches the 100 most recent block from the blockchain.
Otherwise, it fetches 100 blocks prior to the lowest block number already fetched, to backfill any potential gaps in the data.
The commented section provides an option to fetch any new blocks that haven't been fetched yet, up to the most recent block number (block_latest), if the highest fetched block is not the latest one. This ensures the database is up to date with the blockchain.
"""
#n = 100
n=400
if block_lowest_fetched is None or block_highest_fetched is None:
  fetch_blocks(block_latest-n, block_latest, web3)
else:
  fetch_blocks(block_lowest_fetched-n, block_lowest_fetched-1, web3)

'''  if (block_latest != block_highest_fetched):
    fetch_blocks(block_highest_fetched+1, block_latest)'''

print('processing the transactions...')
process_transaction(web3, erc721_transfer, erc1155_transfer_single, erc1155_transfer_batch, etherscan_api_key)
