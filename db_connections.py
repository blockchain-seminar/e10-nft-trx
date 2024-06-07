
import sqlite3 as sql
import pandas as pd
from config import w3

from utils import setup_logger

logger = setup_logger()

# Retrieves aggregated data (like max or min) of block numbers from the 'fetched_blocks' table. Closes the connection after fetching data. Returns None if an error occurs
def get_fetched_blocks(agg):
  try:
    conn = sql.connect("e10.db")
    cursor = conn.cursor()
    query = f"select {agg}(block_number) from fetched_blocks"
    cursor.execute(query)
    block = cursor.fetchone()[0]
    conn.close()
    return block
  except sql.OperationalError as e:
    print("Error:", e)
    return None

# Fetches all records from the 'fetched_transactions' table and returns them as a DataFrame. Closes the connection after fetching data.
def get_fetched_transactions():
  conn = sql.connect("e10.db")
  cursor = conn.cursor()
  df = pd.read_sql_query("SELECT * FROM transactions", conn)
  conn.close()
  return df

def get_marketplaces():
  conn = sql.connect("e10.db")
  cursor = conn.cursor()
  df = pd.read_sql_query("SELECT * FROM marketplaces", conn)
  conn.close()
  return df

# Appends a DataFrame to a specified table within the database. If the table does not exist, it is created. Closes the connection after writing. Prints an error message if an operation fails
def write_to_db(df, table_name):
  try:
    conn = sql.connect("e10.db")
    cursor = conn.cursor()
    cnt = df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
    logger.info(f'INFO: inserted {cnt} rows into table {table_name}') 
    logger.info(df.head())
    conn.close()
  except sql.OperationalError as e:
    print("Error:", e)

def read_from_db(query):
  try:
    logger.info(f'INFO: execute query: {query}') 
    conn = sql.connect("e10.db")
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])
    conn.close()
    return df
  except sql.OperationalError as e:
    print("Error:", e)

def get_latest_blocks():
    """ 
    We retrieve and print the latest block number on the Ethereum blockchain, as well as the minimum and maximum block numbers that we already fetched from the database:
        block_latest holds the number of the most recent block.
        block_lowest_fetched retrieves the smallest block number from the already fetched blocks using the get_fetched_blocks("min") function.
        block_highest_fetched retrieves the largest block number from the already fetched blocks using the get_fetched_blocks("max") function.
        Prints each of these values to provide a current snapshot of block synchronization status with the blockchain.
    """
    block_latest = w3.eth.block_number
    block_lowest_fetched = get_fetched_blocks("min")
    block_highest_fetched = get_fetched_blocks("max")

    logger.info('block_latest ->', block_latest)
    logger.info('block_lowest_fetched ->', block_lowest_fetched)
    logger.info('block_highest_fetched ->', block_highest_fetched)
    
    return block_latest, block_lowest_fetched, block_highest_fetched
