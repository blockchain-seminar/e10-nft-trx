from db_connections import get_fetched_transactions, write_to_db
import time
from data_processing import determine_contract_type, get_traded_price_and_currency, parse_int_from_data
from tqdm import tqdm
from web3 import Web3

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8547"))

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


    df_tx = get_fetched_transactions()
    data = []
    print('starting transaction loops')
    for tx_hash in tqdm(df_tx['hash']):
        time.sleep(0.5)
        try:
            print('fetching receipt')
            receipt = web3.eth.get_transaction_receipt(tx_hash)

            for log in receipt.logs:
                print('iterating logs...')
                if log['topics'][0].hex() in [erc721_transfer, erc1155_transfer_single, erc1155_transfer_batch]:
                    print('its an erc contract which is relevant')
                    traded_price_eth, currency = get_traded_price_and_currency(tx_hash, log, web3, etherscan_api_key)
                    #from_address = web3.to_checksum_address('0x' + log['topics'][1].hex()[-40:]) # @TODO: I don't understand it, maybe we need it above as well.
                    #to_address = web3.to_checksum_address('0x' + log['topics'][2].hex()[-40:])
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
                        #"Timestamp": formatted_timestamp,
                        "hash": tx_hash,
                        #"Block Number": receipt.blockNumber,
                        "log_index": log_index,
                        #"From Address": from_address,
                        #"To Address": to_address,
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
            print(f"Error processing transaction {tx_hash}: {e}")

    print('transforming into dataframe')
    df_receipts = pd.DataFrame(data)
    df_receipts['token_id'] = df_receipts['token_id'].apply(lambda x: str(x)) # convert to string because "OverflowError: Python int too large to convert to SQLite INTEGER"
    df_receipts['log_index'] = df_receipts['log_index'].apply(lambda x: str(x))
    df_receipts['price'] = df_receipts['price'].apply(lambda x: str(x))

    print('writing...')
    write_to_db(df_receipts, 'receipts')
