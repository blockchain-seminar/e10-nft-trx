`main.py`
* Usage: python3 main.py --mode <mode> [--n <n>]
* Example: python3 main.py --mode 1 --n 10000
* Parameters:
    *    --mode <mode> (required)
        Specifies the mode of operation. Acceptable values are:
        1 - fetch and store new blocks and transactions for specified param n (default)
        2 - fetch and store the receipts and logs of transactions in e10.db
        3 - final processing of data in e.10db

    *  --n <n> (optional)
        Number of blocks to fetch, required when mode is 1  

`init_db.sql`
* create e10.db
* execute to initialize db with populated tables marketplaces, abi_event and view v_nft_price_data 

`config.py`
* specify node to connect to (url)

`.env.sample`
*  copy this document and save it as `.env` with your keys
