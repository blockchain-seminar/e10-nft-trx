from db_connections import write_to_db
from utils import setup_logger, find_key_by_value
from config import contract_abi, contract_address, etherscan_api_key
from web3 import Web3
import datetime
from tqdm import tqdm
import pandas as pd
from requests.exceptions import HTTPError
import time

from utils.data_processing import erc721_transfer, erc1155_transfer_single, erc1155_transfer_batch, \
    get_traded_price_and_currency, parse_int_from_data, determine_contract_type

logger = setup_logger()


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
    # TODO: DANI, CHANGE TO DYNAMIC APPROACH
    contract = {}
    for protocol in contract_address:
        contract[protocol] = (web3.eth.contract(address=contract_address[protocol], abi=contract_abi[protocol]))

    blocks_fetched = []
    transactions = []
    logger.info('START: fetching blocks ...')
    for block_number in tqdm(range(block_from, block_to)):
        try:
            logger.info(f'start fetch block {block_number}')
            block = web3.eth.get_block(block_number, full_transactions=True)
            logger.info('appending transaction data...')
            for tx in block.transactions:
                # @TGU
                protocol = find_key_by_value(contract_address, tx.to)

                try:
                    print('fetching receipt')
                    receipt = web3.eth.get_transaction_receipt(tx.trx_hash)
                    timestamp = pd.to_datetime(block.timestamp, unit='s')
                    formatted_timestamp = datetime.strftime(timestamp, '%Y-%m-%d %H:%M:%S')

                    for log in receipt.logs:
                        print('iterating logs...')
                        if protocol is not None:
                            func_obj, func_params = contract[protocol].decode_function_input(tx["input"])
                            if log['topics'][0].hex() in [erc721_transfer, erc1155_transfer_single,
                                                          erc1155_transfer_batch]:
                                print('its an erc contract which is relevant')
                                traded_price_eth, currency = get_traded_price_and_currency(tx.trx_hash, log, web3,
                                                                                           etherscan_api_key)
                                from_address = web3.to_checksum_address('0x' + log['topics'][1].hex()[-40:])
                                to_address = web3.to_checksum_address('0x' + log['topics'][2].hex()[-40:])
                                token_id = parse_int_from_data(log['data']) if log['data'] else "Data Not Available"
                                value = parse_int_from_data(log['data'][64:]) if len(log['data']) > 64 else 0
                                log_index = log.logIndex
                                contract_type = determine_contract_type(log, erc721_transfer, erc1155_transfer_single,
                                                                        erc1155_transfer_batch)

                                # TODO: Functions for NFT Item and Collection
                                nft_item = f"NFT Item for {token_id}"
                                nft_collection = f"NFT Collection for {contract_type}"
                                platform = "Platform based on contract address"  # Example placeholder

                                try:
                                    # Prepare data dictionary
                                    record = {
                                        'fetched_dt': datetime.datetime.now(),
                                        "d_contract": contract_type,
                                        "d_timestamp": formatted_timestamp,
                                        "d_hash": tx.trx_hash,
                                        'trx_hash': tx['hash'].hex(),
                                        "d_block_number": receipt.blockNumber,
                                        'block_number': tx['blockNumber'],
                                        'block_hash': tx['blockHash'].hex(),
                                        "d_log_index": log_index,
                                        "d_from_address": from_address,
                                        'trx_initiator': tx['from'],
                                        "d_to_address": to_address,
                                        'marketplace_address': tx['to'],
                                        "d_token_id": token_id,
                                        "d_value": value,
                                        'trx_value': tx['value'],
                                        "d_currency": currency,
                                        "d_price": traded_price_eth,
                                        "d_platform": platform,
                                        "d_nft_item": nft_item,
                                        "d_nft_collection": nft_collection,
                                        'trx_value_eth': float(Web3.from_wei(tx.value, 'ether')),
                                        # TODO if trx_value is in wei. we need read it from the logs (transaction_processing.py does it I think)
                                        'token_id': func_params['']['offerIdentifier'],
                                        'nft_contract': func_params['']['offerToken'],
                                        'token_qty': func_params['']['offerAmount'],
                                        'nft_marketplace': protocol
                                    }
                                    print('collected data: ')
                                    print(record)
                                    transactions.append(record)
                                except (TypeError, AttributeError, KeyError) as e:
                                    # TODO deal with different input data format (different contracts = different input?)
                                    logger.exception('Exception occurred. Input data not appendend', block_number, ' ',
                                                     tx['hash'].hex())
                                    record = {
                                        'fetched_dt': datetime.datetime.now(),
                                        "d_contract": contract_type,
                                        "d_timestamp": formatted_timestamp,
                                        "d_hash": tx.trx_hash,
                                        'trx_hash': tx['hash'].hex(),
                                        "d_block_number": receipt.blockNumber,
                                        'block_number': tx['blockNumber'],
                                        'block_hash': tx['blockHash'].hex(),
                                        "d_log_index": log_index,
                                        "d_from_address": from_address,
                                        'trx_initiator': tx['from'],
                                        "d_to_address": to_address,
                                        'marketplace_address': tx['to'],
                                        "d_token_id": token_id,
                                        "d_value": value,
                                        'trx_value': tx['value'],
                                        "d_currency": currency,
                                        "d_price": traded_price_eth,
                                        "d_platform": platform,
                                        "d_nft_item": nft_item,
                                        "d_nft_collection": nft_collection,
                                        'trx_value_eth': float(Web3.from_wei(tx.value, 'ether')),
                                        # TODO if trx_value is in wei. we need read it from the logs (transaction_processing.py does it I think)
                                        'token_id': None,
                                        'nft_contract': None,
                                        'token_qty': None,
                                        'nft_marketplace': protocol
                                    }
                                    transactions.append(record)

                    blocks_fetched.append({'fetched_dt': datetime.datetime.now(), 'block_number': block.number})
                    logger.info(f'end fetch block {block_number}')
                except Exception as e:
                    print(f"Error processing transaction {tx.trx_hash}: {e}")

        except HTTPError as e:
            if e.response.status_code == 429:
                time.sleep(60)  # 10 Requests/Second, 100,000 Total Requests/Day (INFURA)

    df_blocks = pd.DataFrame(blocks_fetched)
    df_blocks.set_index('block_number', inplace=True)
    logger.info('writing fetch info into database')
    write_to_db(df_blocks, 'fetched_blocks')

    df_transactions = pd.DataFrame(transactions)
    df_transactions.set_index('trx_hash', inplace=True)

    # to avoid overflow errors with sql lite db. TODO find better solution
    for column in ['token_qty', 'token_contract', 'token_id']:
        df_transactions[column] = df_transactions[column].astype(str)

    logger.info('writing transactions into database')
    write_to_db(df_transactions, 'transactions')
    logger.info('END: fetching blocks completed.')
