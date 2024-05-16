from db_connections import write_to_db
from utils import setup_logger, find_key_by_value, get_contract_abi
from config import contract_address, web3
from datetime import datetime
from tqdm import tqdm
import pandas as pd
from requests.exceptions import HTTPError
import time

from utility_functions.data_processing import get_traded_price_and_currency, parse_int_from_data, \
    determine_contract_type

logger = setup_logger()


# get all blocks and stuff

def fetch_blocks(block_from, block_to):
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
    contract_abi = get_contract_abi(contract_address)
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
            for tx in tqdm(block.transactions):
                # @TGU
                protocol = find_key_by_value(contract_address, tx.to)

                try:
                    logger.info(f'reading receipt for {block_number} transaction {tx.hash}')
                    receipt = web3.eth.get_transaction_receipt(tx.hash)
                    timestamp = pd.to_datetime(block.timestamp, unit='s')
                    formatted_timestamp = datetime.strftime(timestamp, '%Y-%m-%d %H:%M:%S')

                    for log in receipt.logs:
                        # if protocol is not None: # this only means that we dont have the contract abi or something ... idk
                        # func_obj, func_params = contract[protocol].decode_function_input(tx["input"])

                        contract_type = determine_contract_type(log)
                        if contract_type != "Unknown":

                            # here we should only have transactions which follow the ERC 721 structure
                            logger.info(f'reading an ERC contract from block {block_number} transaction {tx.hash}')
                            traded_price_eth, currency = get_traded_price_and_currency(tx, log)

                            nft_collection = log['address']
                            from_address = log['topics'][1].hex()  # web3.to_checksum_address('0x' + log['topics'][1].hex()[-40:])
                            to_address = log['topics'][2].hex()  # web3.to_checksum_address('0x' + log['topics'][2].hex()[-40:])
                            nft_token_id = parse_int_from_data(log['topics'][3])
                            nonce = tx.get('nonce', None)
                            gas = tx.get('gas', None)
                            gas_price = tx.get('gasPrice', None)
                            chain_id = tx.get('chainId', None)
                            # token_id = parse_int_from_data(log['data']) if log['data'] else "Data Not Available"
                            # value = parse_int_from_data(log['data'][64:]) if len(log['data']) > 64 else 0
                            log_index = log.get('logIndex', None)
                            transaction_index = log.get('transactionIndex', None)

                            # address # nft line (e.g. cyberpunk or what so ever)
                            # topics[0] # signature
                            # topics[1] # from address (old owner) / seller
                            # topics[2] # new owner (to address) / buyer
                            # topics[3] # token id

                            platform = "Platform based on contract address"  # Example placeholder

                            try:
                                # Prepare data dictionary
                                record = {
                                    # transaction information
                                    'fetched_dt': datetime.now(),
                                    "contract": contract_type,
                                    "timestamp": formatted_timestamp,
                                    'transaction_hash': tx['hash'].hex(),
                                    "block_number": receipt.blockNumber,
                                    'block_hash': tx['blockHash'].hex(),

                                    'transaction_initiator': tx['from'],
                                    'transaction_interacted_contract': tx['to'], # could also be market place contract

                                    "nonce": nonce,
                                    "gas_price": gas_price,
                                    "gas": gas,
                                    "chain_id": chain_id,

                                    "log_index": log_index,
                                    "transaction_index": transaction_index,

                                    # nft information
                                    "nft_collection": nft_collection,
                                    "from_address": from_address,
                                    "to_address": to_address,
                                    "nft_token_id": nft_token_id,

                                    'trx_value': tx['value'],
                                    'trx_value_eth': float(web3.from_wei(tx.value, 'ether')),

                                    "transaction_action_value": traded_price_eth,
                                    "transaction_action_currency": currency,

                                    # "value": value,  # always zero... idk if still needed or so

                                    "platform": platform,
                                    # other currency value, not token ID

                                    # 'token_id': func_params['']['offerIdentifier'],
                                    # 'nft_contract': func_params['']['offerToken'],
                                    # 'token_qty': func_params['']['offerAmount'],
                                    'nft_marketplace': protocol
                                }
                                logger.info(f'data collected: {record}')
                                transactions.append(record)
                            except (TypeError, AttributeError, KeyError) as e:
                                # TODO deal with different input data format (different contracts = different input?)
                                logger.exception('Exception occurred. Input data not appended', block_number, ' ',
                                                 tx['hash'].hex())
                                record = {
                                    # transaction information
                                    'fetched_dt': datetime.now(),
                                    "contract": contract_type,
                                    "timestamp": formatted_timestamp,
                                    'transaction_hash': tx['hash'].hex(),
                                    "block_number": receipt.blockNumber,
                                    'block_hash': tx['blockHash'].hex(),

                                    'transaction_initiator': tx['from'],
                                    'transaction_interacted_contract': tx['to'],

                                    "nonce": nonce,
                                    "gasPrice": gas_price,
                                    "gas": gas,
                                    "chainId": chain_id,

                                    "log_index": log_index,
                                    "transaction_index": transaction_index,

                                    # nft information
                                    "nft_collection": nft_collection,
                                    "from_address": from_address,
                                    "to_address": to_address,
                                    "nft_token_id": nft_token_id,

                                    'trx_value': tx['value'],
                                    'trx_value_eth': float(web3.from_wei(tx.value, 'ether')),

                                    "transaction_action_value": traded_price_eth,
                                    "transaction_action_currency": currency,

                                    # "value": value,  # always zero... idk if still needed or so

                                    "platform": platform,
                                    # other currency value, not token ID

                                    # 'token_id': func_params['']['offerIdentifier'],
                                    # 'nft_contract': func_params['']['offerToken'],
                                    # 'token_qty': func_params['']['offerAmount'],
                                    'nft_marketplace': protocol
                                }
                                transactions.append(record)
                        else:
                            logger.info(f'Not a ERC721 or 1155, skipping: {tx.hash}')
                    blocks_fetched.append({'fetched_dt': datetime.now(), 'block_number': block.number})
                    logger.info(f'end fetch block {block_number}')
                except Exception as e:
                    logger.exception('Exception occurred. Input data not appendend', block_number, ' ',
                                     tx['hash'].hex())

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
    for column in ['d_token_id', 'd_price']:
        df_transactions[column] = df_transactions[column].astype(str)

    logger.info('writing transactions into database')
    write_to_db(df_transactions, 'trx')
    logger.info('END: fetching blocks completed.')
