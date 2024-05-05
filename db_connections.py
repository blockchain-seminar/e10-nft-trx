
import sqlite3 as sql
import pandas as pd

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

# Appends a DataFrame to a specified table within the database. If the table does not exist, it is created. Closes the connection after writing. Prints an error message if an operation fails
def write_to_db(df, table_name):
  try:
    conn = sql.connect("e10.db")
    cursor = conn.cursor()
    df.to_sql(name=table_name, con=conn, if_exists='append')
    print('writing to database')
    print(df)
    conn.close()
  except sql.OperationalError as e:
    print("Error:", e)
