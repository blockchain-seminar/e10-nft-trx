from db_connections import get_marketplaces, read_from_db, write_to_db
from utils import setup_logger
from datetime import datetime
from tqdm import tqdm
import pandas as pd
from config import w3

from utility_functions.data_processing import get_traded_price_and_currency, parse_int_from_data, \
   determine_contract_type

logger = setup_logger()
marketplaces = get_marketplaces()

def filter_transactions_by_marketplace(transactions):
    try:
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
        for block_number in tqdm(range(block_from, block_to+1)):
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
    '''
    processing the receipts from the logs, flatten it and storing to DB
    '''
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

def enrich():
    '''
    For all the raw data that hasn't been enriched and stored in table nft_price_data, we fetch contract_type and nft information
    '''
    df = read_from_db('select l.*, t.to_address, t.from_address, t.value from receipt_logs l left join transactions t on t.transaction_hash = l.transaction_hash where t.transaction_hash not in (select distinct transaction_hash from nft_price_data);')
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        temp = {}
        contract_type = determine_contract_type(row['address'])
        traded_price_eth, currency, from_address, to_address,nft_collection,nft_token_id = None, None, None, None, None, None
        if contract_type == "Unknown":
            traded_price_eth, currency = get_traded_price_and_currency(row['value'], row['topics_0'],row['address'],row['data'])
        else:
            from_address = row['topics_1']
            to_address = row['topics_2']  # web3.to_checksum_address('0x' + log['topics'][2].hex()[-40:])
            try:
                if pd.isnull(row['topics_3']):
                    # if there are 3 attributes then the "TO address becomes the nft_collection"
                    # the nft_token_id also does not exist.
                    nft_collection = row['to_address']
                    nft_token_id = None
                else:
                    nft_collection = row['address']
                    nft_token_id = parse_int_from_data(row['topics_3'])
            except Exception as e:
                #logger.exception(e)
                pass


        #if contract_type in ["ERC-721", "ERC-1155"]: 
        temp = {
            'create_dt': datetime.now(),
            'log_index': row['log_index'],
            'transaction_hash': row['transaction_hash'],
            'contract_type': contract_type,
            'transaction_value': row['value'],
            'transaction_value_eth': float(w3.from_wei(row['value'], 'ether')),
            'transaction_action_value':traded_price_eth,
            'transaction_action_currency':currency,
            'transaction_initiator': row['from_address'],
            'transaction_interacted_contract': row['to_address'], 
            'nft_from_address': from_address,
            'nft_to_address': to_address,
            'nft_collection': nft_collection,
            'nft_token_id': nft_token_id
        }
        
         # to avoid overflow errors with sql lite db. TODO find better solution
        df_transactions = pd.DataFrame([temp])
        
        for column in ['nft_token_id', 'transaction_action_value']:
            df_transactions[column] = df_transactions.apply(lambda x: str(x[column]) if x[column] is not None else None, axis=1)
            
        write_to_db(df_transactions, 'nft_price_data')

        # TODO: TGU create view in db and join marketplace?   
       