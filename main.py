from config import infura_api_key, web3
from data_processing import fetch_blocks
from db_connections import get_latest_blocks


def initialize():
    # TODO
    pass


def main():
    block_latest, block_lowest_fetched, block_highest_fetched = get_latest_blocks(web3)

    n = 10
    if block_lowest_fetched is None or block_highest_fetched is None:
        fetch_blocks(block_latest - n, block_latest)
    else:
        fetch_blocks(block_lowest_fetched - n, block_lowest_fetched - 1)


if __name__ == "__main__":
    initialize()
    main()
    print("end")
