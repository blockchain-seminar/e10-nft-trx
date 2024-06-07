from db_connections import get_marketplaces, write_to_db
from utils import setup_logger, find_key_by_value, get_contract_abi
from datetime import datetime
from tqdm import tqdm
import pandas as pd
from requests.exceptions import HTTPError
import time
from config import w3

from utility_functions.data_processing import get_traded_price_and_currency, parse_int_from_data, \
   determine_contract_type

logger = setup_logger()
marketplaces = get_marketplaces()

def filter_transactions_by_marketplace(transactions):
    try: #TODO
        transaction_data = []
        for transaction in transactions:
            if str(transaction['to']).lower() in marketplaces['contract_address'].values:
                temp = {'fetched_dt': datetime.now(),
                        'transaction_hash': transaction['hash'].hex(),
                        'block_number': transaction['blockNumber'],
                        'chain_id': transaction['chainId'],
                        'from_address': transaction['from'],
                        'gas': transaction['gas'],
                        'gas_price': transaction['gasPrice'],
                        'input_data': transaction['input'],
                        'max_fee_per_gas': transaction['maxFeePerGas'],
                        'max_priority_fee_per_gas': transaction['maxPriorityFeePerGas'],
                        'nonce': transaction['nonce'],
                        'r': transaction['r'],
                        's': transaction['s'],
                        'to_address': transaction['to'],
                        'transaction_index': transaction['transactionIndex'],
                        'transaction_type': transaction['type'],
                        'v': transaction['v'],
                        'value': transaction['value'],
                        'y_parity': transaction['yParity']
                        }
                transaction_data.append(temp)
            df_transaction = pd.DataFrame(transaction_data)
        return df_transaction
    except Exception as e:
        logger.exception(e)
        


def fetch_and_store_transactions_in_block_range(block_from, block_to):
    logger.info('START: fetching_and_store_transactions_in_block_range ...')
    try:
        for block_number in tqdm(range(block_from, block_to)):
            block = w3.eth.get_block(block_number, full_transactions=True)
            write_to_db(pd.DataFrame({'fetched_dt': datetime.now(), 'block_number': block.number},index=[0]), 'fetched_blocks')
            df_transactions = filter_transactions_by_marketplace(block.transactions)
            write_to_db(df_transactions, 'transactions')  
        return df_transactions
    except Exception as e:
        logger.exception(e)
        pass
    finally:
        logger.info('END: fetching_and_store_transactions_in_block_range ...')

def fetch_and_process_receipts(transaction_hash):
    logger.info('START: fetch_and_process_receipts ...')
    try:
        receipt = w3.eth.get_transaction_receipt(transaction_hash)
        process_and_store_receipts(receipt)
    except Exception as e:
        logger.exception(e, transaction_hash)
        pass
    finally:
        logger.info('END: fetch_and_process_receipts ...')

def process_and_store_receipts(receipt):
    logger.info('START:process_and_store_receipts ...')
    try:
        data = {
                'fetched_dt': datetime.now(),
                'transaction_hash': receipt['transactionHash'].hex(),
                'contract_address': receipt['contractAddress'],
                'cumulative_gas_used': receipt['cumulativeGasUsed'],
                'effective_gas_price': receipt['effectiveGasPrice'],
                'from': receipt['from'],
                'gas_used': receipt['gasUsed'],
                'logs_bloom': receipt['logsBloom'].hex(),
                'status':receipt['status'],
                'to': receipt['to'],
                'transaction_index': receipt['transactionIndex'],
                'type': receipt['type']
                }
        process_and_store_receipt_logs(receipt['logs'])
        write_to_db(pd.DataFrame(data,index=[0]), 'receipts')
    except Exception as e:
        logger.exception(e, receipt['blockNumber'], ' ', receipt['transactionHash'].hex())
        pass
    finally:
        logger.info('END: process_and_store_receipts ...')
    
def process_and_store_receipt_logs(logs):
    logger.info('START: process_and_store_receipt_logs ...')
    try:
        data = []
        for log in logs:               
            temp = {
                'fetched_dt': datetime.now(),
                'log_index': log['logIndex'],
                'transaction_hash': log['transactionHash'].hex(),
                'transaction_index': log['transactionIndex'],
                'address': log['address'],
                'data': log['data'].hex(),
                'removed': log['removed'],
            }
        
            cnt_topic = 0
            for topic in log['topics']:
                temp[f'topics_{cnt_topic}'] = topic.hex()
                cnt_topic += 1
                    
            data.append(temp)
        write_to_db(pd.DataFrame(data), 'receipt_logs')
    except Exception as e:
        logger.exception(e)
        pass
    finally:
        logger.info('END: process_and_store_receipt_logs ...')

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
    #marketplaces = get_contract_addresses()
    #contract_abi = get_contract_abi(marketplaces)
   # for address in marketplaces['contract_address']:
    #    contract[address] = (web3.eth.contract(address=address, abi=contract_abi[address]))

    blocks_fetched = []
    transactions = []
    logger.info('START: fetching blocks ...')
    for block_number in tqdm(range(block_from, block_to)):
        try:
            logger.info(f'start fetch block {block_number}')
            block = w3.eth.get_block(block_number, full_transactions=True)
            logger.info('appending transaction data...')
            for tx in tqdm(block.transactions):
            
                #protocol = find_key_by_value(contract_address, tx.to)
                # just fetch from the marketplaces specified
                if str(tx['to']).lower() in marketplaces['contract_address'].values:
                    try:
                        logger.info(f'reading receipt for {block_number} transaction {tx.hash.hex()}')
                        receipt = w3.eth.get_transaction_receipt(tx.hash)
                        timestamp = pd.to_datetime(block.timestamp, unit='s')
                        formatted_timestamp = datetime.strftime(timestamp, '%Y-%m-%d %H:%M:%S')
                        nonce = tx.get('nonce', None)
                        gas = tx.get('gas', None)
                        gas_price = tx.get('gasPrice', None)
                        chain_id = tx.get('chainId', None)
                        has_nft = False
                        for log in receipt.logs:
                            contract_type = determine_contract_type(log)
                            if contract_type in ["ERC-721", "ERC-1155"]:
                                has_nft = True
                                break

                        if has_nft:
                            for log in receipt.logs:

                                contract_type = determine_contract_type(log)

                                # here we should only have transactions which follow the ERC 721 structure
                                logger.info(f'reading an ERC contract from block {block_number} transaction {tx.hash}')
                                if contract_type == "Unknown":
                                    traded_price_eth, currency = get_traded_price_and_currency(tx, log)
                                else:
                                    traded_price_eth, currency = None, None

                                if len(log['topics']) == 4:
                                    nft_collection = log['address']
                                    from_address = log['topics'][1].hex()  # web3.to_checksum_address('0x' + log['topics'][1].hex()[-40:])
                                    to_address = log['topics'][2].hex()  # web3.to_checksum_address('0x' + log['topics'][2].hex()[-40:])
                                    nft_token_id = parse_int_from_data(log['topics'][3])
                                elif len(log['topics']) == 3:
                                    # if there are 3 attributes then the "TO address becomes the nft_collection"
                                    # the nft_token_id also does not exist.
                                    nft_collection = tx['to']
                                    from_address = log['topics'][1].hex()  # web3.to_checksum_address('0x' + log['topics'][1].hex()[-40:])
                                    to_address = log['topics'][2].hex()  # web3.to_checksum_address('0x' + log['topics'][2].hex()[-40:])
                                    nft_token_id = "In existent..."
                                else:
                                    nft_collection = log['address']
                                    from_address = log['topics'][1].hex()  # web3.to_checksum_address('0x' + log['topics'][1].hex()[-40:])
                                    to_address = log['topics'][2].hex()  # web3.to_checksum_address('0x' + log['topics'][2].hex()[-40:])
                                    nft_token_id = parse_int_from_data(log['topics'][3])
                                    print("Attention")

                                    # if there are 2 attributes then the
                                    #

                                # token_id = parse_int_from_data(log['data']) if log['data'] else "Data Not Available"
                                # value = parse_int_from_data(log['data'][64:]) if len(log['data']) > 64 else 0
                                log_index = log.get('logIndex', None)
                                transaction_index = log.get('transactionIndex', None)

                                # address # nft line (e.g. cyberpunk or what so ever)
                                # topics[0] # signature
                                # topics[1] # from address (old owner) / seller
                                # topics[2] # new owner (to address) / buyer
                                # topics[3] # token id

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
                                        'trx_value_eth': float(w3.from_wei(tx.value, 'ether')),

                                        "transaction_action_value": traded_price_eth,
                                        "transaction_action_currency": currency,

                                        # "value": value,  # always zero... idk if still needed or so

                                        #"platform": platform, # TODO: TGU create view in db and join info.
                                        # other currency value, not token ID

                                        # 'token_id': func_params['']['offerIdentifier'],
                                        # 'nft_contract': func_params['']['offerToken'],
                                        # 'token_qty': func_params['']['offerAmount'],
                                        #'nft_marketplace': protocol
                                    }
                                    logger.info(f'data collected: {record}')
                                    transactions.append(record)
                                except (TypeError, AttributeError, KeyError) as e:
                                    # TODO deal with different input data format (different contracts = different input?)
                                    logger.exception(e, block_number, ' ', tx['hash'].hex())
                                    print("ATTENTION!!")
                    except Exception as e:
                        logger.exception(e, block_number, ' ', tx['hash'].hex())

            blocks_fetched.append({'fetched_dt': datetime.now(), 'block_number': block.number})
            logger.info(f'end fetch block {block_number}')
        except HTTPError as e:
            if e.response.status_code == 429:
                time.sleep(60)  # 10 Requests/Second, 100,000 Total Requests/Day (INFURA)

    df_blocks = pd.DataFrame(blocks_fetched)
    df_blocks.set_index('block_number', inplace=True)
    logger.info('writing fetch info into database')
    write_to_db(df_blocks, 'fetched_blocks')

    df_transactions = pd.DataFrame(transactions)
    if not df_transactions.empty:
        df_transactions.set_index('transaction_hash', inplace=True)

        # to avoid overflow errors with sql lite db. TODO find better solution
        for column in ['nft_token_id', 'transaction_action_value']:
            df_transactions[column] = df_transactions[column].astype(str)

        logger.info('writing transactions into database')
        write_to_db(df_transactions, 'transactions2')
        logger.info('END: fetching blocks completed.')
