from data_processing import enrich, fetch_and_process_receipts, fetch_and_store_transactions_in_block_range
from db_connections import get_latest_blocks, read_from_db
from utils import setup_logger

def initialize():
    # TODO
    pass

def main(mode = 1):
    logger = setup_logger()
    n = 10 # for mode 3
    mode = mode # 1 = fetch and store new blocks and transactions for specified n; 2 = fetch and store the receipts and logs; 3 = final processing of data

    if mode == 1:
        block_latest, block_lowest_fetched, block_highest_fetched = get_latest_blocks()
        if block_lowest_fetched is None or block_highest_fetched is None:
            fetch_and_store_transactions_in_block_range(block_from=(block_latest - n), block_to=block_latest)
        else:
            fetch_and_store_transactions_in_block_range(block_from=(block_lowest_fetched - n), block_to=(block_lowest_fetched - 1))   
    elif mode == 2:
        df = read_from_db('select distinct transaction_hash from transactions where transaction_hash not in (select transaction_hash from receipts)')
        for transaction_hash in df['transaction_hash']:
            try:
                fetch_and_process_receipts(transaction_hash)
            except Exception as e:
                logger.exception(e, transaction_hash)
    elif mode == 3:
        enrich()  

if __name__ == "__main__":
    initialize()
    main()
