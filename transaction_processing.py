from db_connections import get_fetched_transactions, write_to_db
import time
from data_processing import determine_contract_type, get_traded_price_and_currency, parse_int_from_data
from tqdm import tqdm
from web3 import Web3
import pandas as pd
from utility_functions import fetch_contract_abi

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8547"))

'''
TODO
A Transaction can be in different currencies (depends on seaport version) --> need to read from payment token
'''


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
            erc20_abi = fetch_contract_abi(token_contract, etherscan_api_key)
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

def process_transaction(web3, erc721_transfer, erc1155_transfer_single, erc1155_transfer_batch, etherscan_api_key): 
    """ 
    This script processes Ethereum transactions to extract and analyze NFT-related data:
        - df_tx: DataFrame containing transaction hashes from the DB.
        - We iterate over these hashes, pausing slightly between each to manage request rates.
        - For each transaction, it fetches the receipt and parses each log:
            - It checks if the log pertains to an ERC-721 or ERC-1155 transfer.
            - Retrieves the traded price in ETH and the currency used.
            - Parses relevant data from the log to identify token ID and other values.
            - Uses predefined functions to assign types and other metadata (like item details and collection info) based on the log data.
            - Records such as transaction hash, log index, token ID, and other derived information are compiled into a record and appended to a list.
    => The resulting DataFrame df_receipts converts certain fields to strings to accommodate database constraints and writes this data to a database table named 'receipts'.
    """
    print('START: processing the transactions...')

    df_tx = get_fetched_transactions()
    print(df_tx)
    data = []
    print('starting transaction loops')
    for trx_hash in tqdm(df_tx['trx_hash']):
        time.sleep(0.5)
        try:
            print('fetching receipt')
            receipt = web3.eth.get_transaction_receipt(trx_hash)
            block = web3.eth.get_block(receipt.blockNumber)
            timestamp = pd.to_datetime(block.timestamp, unit='s')
            formatted_timestamp = datetime.strftime(timestamp, '%Y-%m-%d %H:%M:%S')

            for log in receipt.logs:
                print('iterating logs...')
                if log['topics'][0].hex() in [erc721_transfer, erc1155_transfer_single, erc1155_transfer_batch]:
                    print('its an erc contract which is relevant')
                    traded_price_eth, currency = get_traded_price_and_currency(trx_hash, log, web3, etherscan_api_key)
                    from_address = web3.to_checksum_address('0x' + log['topics'][1].hex()[-40:])
                    to_address = web3.to_checksum_address('0x' + log['topics'][2].hex()[-40:])
                    token_id = parse_int_from_data(log['data']) if log['data'] else "Data Not Available"
                    value = parse_int_from_data(log['data'][64:]) if len(log['data']) > 64 else 0
                    log_index = log.logIndex
                    contract_type = determine_contract_type(log, erc721_transfer, erc1155_transfer_single, erc1155_transfer_batch)

                    # TODO: Functions for NFT Item and Collection
                    nft_item = f"NFT Item for {token_id}"
                    nft_collection = f"NFT Collection for {contract_type}"
                    platform = "Platform based on contract address"  # Example placeholder

                    
                    # Prepare data dictionary
                    record = {
                        "contract": contract_type,
                        "Timestamp": formatted_timestamp,
                        "hash": trx_hash,
                        "Block Number": receipt.blockNumber,
                        "log_index": log_index,
                        "From Address": from_address,
                        "To Address": to_address,
                        "token_id": token_id,
                        "value": value,
                        "currency": currency,
                        "price": traded_price_eth,
                        "platform": platform,
                        "nft_item": nft_item,
                        "nft_collection": nft_collection
                    }
                    print('collected data: ')
                    print(record)
                    # Append data to CSV
                    # append_to_csv(data, filename)
                    data.append(record)

        except Exception as e:
            print(f"Error processing transaction {trx_hash}: {e}")

    print('transforming into dataframe')
    df_receipts = pd.DataFrame(data)
    df_receipts['token_id'] = df_receipts['token_id'].apply(lambda x: str(x)) # convert to string because "OverflowError: Python int too large to convert to SQLite INTEGER"
    df_receipts['log_index'] = df_receipts['log_index'].apply(lambda x: str(x))
    df_receipts['price'] = df_receipts['price'].apply(lambda x: str(x))

    print('writing...')
    write_to_db(df_receipts, 'receipts')
