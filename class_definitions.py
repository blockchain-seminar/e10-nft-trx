from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, TEXT, DATE

db = SQLAlchemy()

class Transaction(db.Model):
    __tablename__ = 'transactions'
    fetched_dt = Column(TIMESTAMP)
    transaction_hash = Column(TEXT, primary_key=True)
    block_number = Column(Integer)
    chain_id = Column(Integer)
    from_address = Column(TEXT)
    gas = Column(Integer)
    gas_price = Column(Integer)
    input_data = Column(TEXT)
    max_fee_per_gas = Column(Integer)
    max_priority_fee_per_gas = Column(Integer)
    nonce = Column(Integer)
    r = Column(TEXT)
    s = Column(TEXT)
    to_address = Column(TEXT)
    transaction_index = Column(Integer)
    transaction_type = Column(Integer)
    v = Column(Integer)
    value = Column(Integer)
    y_parity = Column(Integer)

class VnftPriceData(db.Model):
    __tablename__ = 'v_nft_price_data'
    create_dt = Column(TIMESTAMP)
    log_index = Column(Integer, primary_key=True)
    transaction_hash = Column(TEXT)
    contract_type = Column(TEXT)
    transaction_value = Column(Integer)
    transaction_value_eth = Column(Float)
    transaction_action_value = Column(TEXT)
    transaction_action_currency = Column(TEXT)
    transaction_initiator = Column(TEXT)
    transaction_interacted_contract = Column(TEXT)
    nft_from_address = Column(TEXT)
    nft_to_address = Column(TEXT)
    nft_collection = Column(TEXT)
    nft_token_id = Column(TEXT)
    marketplace = Column(TEXT)

class Marketplace(db.Model):
    __tablename__ = 'marketplaces'
    contract_address = Column(TEXT, primary_key=True)
    protocol = Column(TEXT)
    name = Column(TEXT)
    version = Column(String(5))  # Assuming this is a string type such as '1.0'
    create_dt = Column(DATE)

class FetchedBlock(db.Model):
    __tablename__ = 'fetched_blocks'
    fetched_dt = Column(TIMESTAMP, primary_key=True)
    block_number = Column(Integer)

class ABIEvent(db.Model):
    __tablename__ = 'abi_events'
    anonymous = Column(Integer)
    name = Column(TEXT)
    type = Column(TEXT)
    contract_address = Column(TEXT)
    id = Column(Integer, primary_key=True)
    input_indexed = Column(Integer)
    input_internalType = Column(TEXT)
    input_name = Column(TEXT)
    input_type = Column(TEXT)
    input_id = Column(Integer)
