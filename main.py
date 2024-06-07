from data_processing import fetch_and_process_receipts, fetch_and_store_transactions_in_block_range
from db_connections import get_latest_blocks, get_marketplaces, read_from_db, write_to_db
from utils import setup_logger



def initialize():
    # TODO
    pass

def main():
    logger = setup_logger()
    
    block_latest, block_lowest_fetched, block_highest_fetched = get_latest_blocks()
    n = 5
    if block_lowest_fetched is None or block_highest_fetched is None:
        fetch_and_store_transactions_in_block_range(block_from=(block_latest - n), block_to=block_latest)
    else:
        fetch_and_store_transactions_in_block_range(block_from=(block_lowest_fetched - n), block_to=(block_lowest_fetched - 1))
      
    df = read_from_db('select distinct transaction_hash from transactions where transaction_hash not in (select transaction_hash from receipts)')
    for transaction_hash in df['transaction_hash']:
        try:
            fetch_and_process_receipts(transaction_hash)
        except Exception as e:
            logger.exception(e, transaction_hash)

    #fetch_and_store_transactions_in_block_range(block_from=19135533,block_to=19135535)
    #fetch_and_process_receipts('0xc96a6595a4f009732c99d4df4d4b4a4997eb5d495151859158fb796e7793b184')


if __name__ == "__main__":
    initialize()
    main()
    print("end")
