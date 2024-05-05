from db_connections import write_to_db
from web3 import Web3
import datetime
from tqdm import tqdm
import pandas as pd
from requests.exceptions import HTTPError
import time
import functools
import requests

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8547"))

# get all blocks and stuff

def fetch_blocks(block_from, block_to, web3):

  """
    The function fetch_blocks(block_from, block_to), fetches blocks and their transactions from the Ethereum blockchain between specified block numbers:
    - Iterates over each block number in the specified range.
    - For each block, it retrieves the block details including all transactions (with full_transactions=True).
    - If an HTTP error with status code 429 occurs (rate limit exceeded), it pauses execution for 60 seconds.
    - It stores each block's number and the current timestamp in blocks_fetched.
    - Transactions are stored separately, with specific modifications like removing the 'accessList' column and converting transaction values to strings to prevent data type issues with SQLite.
    - Both blocks and transactions are saved to their respective tables in a SQLite database using the write_to_db function.
    - The transactions DataFrame can be returned for further processing or inspection (currently commented out).
  """
  print('fetch block start...')
  blocks_fetched = []
  transactions = []
  print('iterating through blocks...')
  for block_number in tqdm(range(block_from, block_to)):
    try:
      block = web3.eth.get_block(block_number, full_transactions=True)
      print('appending transactions in blocks...')
      for tx in tqdm(block.transactions):
          transactions.append(tx)
      
      print('block is fetched and will be appended...')
      print(block)
      blocks_fetched.append({'block_number': block.number,'timestamp': datetime.datetime.now()})
    except HTTPError as e:
              if e.response.status_code == 429:
                time.sleep(60) # 10 Requests/Second, 100,000 Total Requests/Day

  print('blcok iteration done')
  df_blocks = pd.DataFrame(blocks_fetched)
  df_blocks.set_index('block_number', inplace=True)
  print('writing into fetch blcoks table...')
  write_to_db(df_blocks, 'fetched_blocks')

  print('creating transactions df')
  df_transactions = pd.DataFrame(transactions)
  try:
    df_transactions.drop(columns=['accessList'], inplace=True)
    df_transactions.drop(columns=['blobVersionedHashes'], inplace=True)
  except:
    pass
  print('df transaction drops done')
  df_transactions['value'] = df_transactions['value'].apply(lambda x: str(x)) # convert to string because "OverflowError: Python int too large to convert to SQLite INTEGER"
  print('writing into database')
  write_to_db(df_transactions, 'transactions')
  print('fetch blcoks completed.')
  # return df_transactions



""" 
    Ethereum smart contracts are identified as either ERC-721 or ERC-1155 based on the event signature hashes from their logs:
    - erc721_transfer, erc1155_transfer_single, and erc1155_transfer_batch store the hashed signatures of transfer events for ERC-721 and ERC-1155 contracts, respectively.
    - determine_contract_type(log) compares the hash of the first topic in the log to the stored hashes to determine if the event corresponds to an ERC-721 or ERC-1155 transfer, or if it's from an unknown contract type.
"""


# Event signature hashes for ERC-721 and ERC-1155 Transfer events
erc721_transfer = Web3.keccak(text='Transfer(address,address,uint256)').hex()
erc1155_transfer_single = Web3.keccak(text='TransferSingle(address,address,address,uint256,uint256)').hex()
erc1155_transfer_batch = Web3.keccak(text='TransferBatch(address,address,address,uint256[],uint256[])').hex()


def determine_contract_type(log, erc721_transfer, erc1155_transfer_single, erc1155_transfer_batch):
    print('determining contract type...')
    if log['topics'][0].hex() == erc721_transfer:
        return 'ERC-721'
    elif log['topics'][0].hex() in [erc1155_transfer_single, erc1155_transfer_batch]:
        return 'ERC-1155'
    else:
        return 'Unknown'
    


def parse_int_from_data(data):
    """
    Converts hexadecimal transaction data into an integer. If conversion fails, it prints an error and returns zero.
    """
    print('parse int start')
    print('converting hexadecimal transaction data into an integer...')
    try:
        # Strip leading zeros and decode data to integer
        print('parse int end')
        return int(data.hex(), 16)
    except ValueError as e:
        print(f"Error parsing data: {data.hex()} with error {str(e)}")
        return 0

# GET ABIs dynamically for currency and price
@functools.lru_cache(maxsize=1000)  # Cache up to 1000 contract ABIs
def get_contract_abi(contract_address, etherscan_api_key):
    """
    Fetches the ABI (Application Binary Interface) for a given contract address from the Etherscan API, utilizing caching to optimize performance. Raises an exception if the ABI cannot be retrieved.
    """
    print('get contract abi start')
    print('fetching the abi for a given contract address from the etherscan api')
    print('currently fetching for : ')
    print(contract_address)
    url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={etherscan_api_key}"
    response = requests.get(url)
    response_json = response.json()

    if response_json['status'] == '1' and response_json['message'] == 'OK':
        contract_abi = response_json['result']
        print('get contract abi end')
        return contract_abi
    else:
        raise Exception("Failed to fetch contract ABI: " + response_json.get('result', 'No additional error info'))

# Get price data from block
def get_traded_price_and_currency(tx_hash, log, web3, etherscan_api_key):
    """ 
    Determines the price and currency of a traded asset in a transaction:
        First checks if the transaction involved ETH directly.
        If the transaction involves an ERC-20 token transfer, it fetches the contract's ABI, calculates the token value from the transfer log, and retrieves the token's symbol and decimal count to compute the traded price in the token's units.
        Handles exceptions and errors that might occur during data retrieval and processing, providing error outputs for troubleshooting.
    """
    print('determining the price and currency of a traded asset in a transactition.')
    traded_price = None
    currency = "ETH"

    # Check if transaction is in eth
    transaction = web3.eth.get_transaction(tx_hash)
    value_eth = transaction.value
    if value_eth > 0:
      traded_price = web3.from_wei(value_eth, 'ether')

    print('transaction to be converted to ETH')
    # If log represents an ERC-20 token transfer, get the token details
    if log['topics'][0].hex() == web3.keccak(text="Transfer(address,address,uint256)").hex():
        token_contract = log['address']
        token_value = parse_int_from_data(log['data']) if log['data'] else "Data Not Available"
        try:
            erc20_abi = get_contract_abi(token_contract, etherscan_api_key)
            token = web3.eth.contract(address=token_contract, abi=erc20_abi)
            symbol = token.functions.symbol().call()
            decimals = token.functions.decimals().call()
            traded_price = token_value / (10 ** decimals)
            currency = symbol
        except Exception as e:
            print(f"Error processing ERC-20 transfer: {e}")
            currency= "Not Available"

    print('traded price and currency end.')
    return traded_price, currency

