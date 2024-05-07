from db_connections import write_to_db
from utils import setup_logger,find_key_by_value
from config import contract_abi, contract_address
from web3 import Web3
import datetime
from tqdm import tqdm
import pandas as pd
from requests.exceptions import HTTPError
import time

log = setup_logger()

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
  # Create contract instances
  contract = {}
  for protocol in contract_address:
    contract[protocol] = (web3.eth.contract(address=contract_address[protocol], abi=contract_abi[protocol]))

  blocks_fetched = []
  transactions = []
  log.info('START: fetching blocks ...')
  for block_number in tqdm(range(block_from, block_to)):
    try:
      log.info(f'start fetch block {block_number}')
      block = web3.eth.get_block(block_number, full_transactions=True)
      log.info('appending transaction data...')
      for tx in block.transactions:
          # @TGU
          protocol = find_key_by_value(contract_address,tx.to)
          if protocol is not None:
              func_obj, func_params = contract[protocol].decode_function_input(tx["input"])
              try:
                transactions.append({
                      'fetched_dt': datetime.datetime.now(),
                      'block_number': tx['blockNumber'],
                      'block_hash': tx['blockHash'].hex(),
                      'trx_hash': tx['hash'].hex(),
                      #'status': 1, # TODO success, failed?
                      'timestamp': None, # TODO
                      'trx_initiator': tx['from'],
                      'marketplace_address': tx['to'],
                      'trx_value': tx['value'],  
                      'trx_value_eth': float(Web3.from_wei(tx.value, 'ether')), # TODO if trx_value is in wei. we need read it from the logs (transaction_processing.py does it I think)
                      'token_id': func_params['']['offerIdentifier'],
                      'nft_contract': func_params['']['offerToken'],
                      'token_qty': func_params['']['offerAmount'],
                      'nft_marketplace': protocol
                      })
              except (TypeError, AttributeError, KeyError) as e:
                  # TODO deal with different input data format (different contracts = different input?)
                  log.exception('Exception occurred. Input data not appendend', block_number, ' ', tx['hash'].hex())
                  transactions.append({
                      'fetched_dt': datetime.datetime.now(),
                      'block_number': tx['blockNumber'],
                      'block_hash': tx['blockHash'].hex(),
                      'trx_hash': tx['hash'].hex(),
                      #'status': 1, # TODO success, failed?
                      'timestamp': None, # TODO
                      'trx_initiator': tx['from'],
                      'marketplace_address': tx['to'],
                      'trx_value': tx['value'],  
                      'trx_value_eth': float(Web3.from_wei(tx.value, 'ether')),
                      'token_id': None,
                      'nft_contract': None,
                      'token_qty': None,
                      'nft_marketplace': protocol
                      })
                      
                  
      blocks_fetched.append({'fetched_dt': datetime.datetime.now(), 'block_number': block.number})
      log.info(f'end fetch block {block_number}')
    except HTTPError as e:
              if e.response.status_code == 429:
                time.sleep(60) # 10 Requests/Second, 100,000 Total Requests/Day (INFURA)

  df_blocks = pd.DataFrame(blocks_fetched)
  df_blocks.set_index('block_number', inplace=True)
  log.info('writing fetch info into database')
  write_to_db(df_blocks, 'fetched_blocks')

  df_transactions = pd.DataFrame(transactions)
  df_transactions.set_index('trx_hash', inplace=True)

  # to avoid overflow errors with sql lite db. TODO find better solution
  for column in ['token_qty','token_contract','token_id']:
    df_transactions[column] = df_transactions[column].astype(str)

  log.info('writing transactions into database')
  write_to_db(df_transactions, 'transactions')
  log.info('END: fetching blocks completed.')