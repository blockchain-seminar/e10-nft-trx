from data_processing import fetch_and_process_receipts, fetch_and_store_transactions_in_block_range
from db_connections import get_latest_blocks, get_marketplaces, write_to_db
from utils import setup_logger



def initialize():
    # TODO
    pass

def main():
    logger = setup_logger()
    block_latest, block_lowest_fetched, block_highest_fetched = get_latest_blocks()
    n = 10000
    if block_lowest_fetched is None or block_highest_fetched is None:
        df_transactions = fetch_and_store_transactions_in_block_range(block_from=(block_latest - n), block_to=block_latest)
    else:
        df_transactions = fetch_and_store_transactions_in_block_range(block_from=(block_lowest_fetched - n), block_to=(block_lowest_fetched - 1))

    try:
        for t in df_transactions['transaction_hash'].values:
            fetch_and_process_receipts(t)
    except Exception as e:
        logger.exception(e, t)
        
    #fetch_and_store_transactions_in_block_range(block_from=19135533,block_to=19135535)
    #fetch_and_process_receipts('0xc96a6595a4f009732c99d4df4d4b4a4997eb5d495151859158fb796e7793b184')


if __name__ == "__main__":
    initialize()
    main()
    print("end")
