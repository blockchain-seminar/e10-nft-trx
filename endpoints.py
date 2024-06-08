from flask import Flask, request, jsonify
from class_definitions import db, Transaction, VnftPriceData, Marketplace, FetchedBlock, ABIEvent
from data_processing import enrich, fetch_and_process_receipts, fetch_and_store_transactions_in_block_range
from db_connections import get_latest_blocks, read_from_db
from utils import setup_logger
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/e10.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
# app.config.from_pyfile('config.py')
logger = setup_logger()

logger.debug("Database path set to: " + app.config['SQLALCHEMY_DATABASE_URI'])
@app.route('/transactions/latest', methods=['GET'])
def get_latest_entries():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    pagination = Transaction.query.order_by(Transaction.fetched_dt.desc()).paginate(page=page, per_page=per_page, error_out=False)
    data = {
        'items': [{'transaction_hash': tx.transaction_hash, 'fetched_dt': tx.fetched_dt, 'block_number': tx.block_number} for tx in pagination.items],
        'total_pages': pagination.pages,
        'current_page': pagination.page
    }
    return jsonify(data)


@app.route('/abis', methods=['GET'])
def get_abis():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    abis = ABIEvent.query.paginate(page=page, per_page=per_page, error_out=False)
    data = [{'name': abi.name, 'type': abi.type, 'contract_address': abi.contract_address} for abi in abis.items]
    return jsonify(data)

@app.route('/blocks/fetched', methods=['GET'])
def get_fetched_blocks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = FetchedBlock.query.order_by(FetchedBlock.fetched_dt.desc()).paginate(page=page, per_page=per_page, error_out=False)
    data = {
        'items': [{'fetched_dt': block.fetched_dt, 'block_number': block.block_number} for block in pagination.items],
        'total_pages': pagination.pages,
        'current_page': pagination.page
    }
    return jsonify(data)

@app.route('/marketplaces', methods=['GET'])
def get_marketplaces():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    marketplaces = Marketplace.query.paginate(page=page, per_page=per_page, error_out=False)
    data = [{'create_dt': mp.create_dt, 'name': mp.name, 'version': mp.version, 'protocol': mp.protocol, 'contract_address': mp.contract_address} for mp in marketplaces.items]
    return jsonify(data)

@app.route('/price_data', methods=['GET'])
def get_price_data():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = VnftPriceData.query.order_by(VnftPriceData.create_dt.desc()).paginate(page=page, per_page=per_page, error_out=False)
    data = [{
        column.name: getattr(entry, column.name) for column in entry.__table__.columns
    } for entry in pagination.items]
    return jsonify({
        'items': data,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })

def binary_to_hex(value):
    return value.hex() if isinstance(value, bytes) else value
@app.route('/transactions/<transaction_hash>', methods=['GET'])
def get_transaction_details(transaction_hash):
    transaction = Transaction.query.filter_by(transaction_hash=transaction_hash).first()
    if transaction:
        data = {col: binary_to_hex(getattr(transaction, col)) for col in transaction.__table__.columns.keys()}
        return jsonify(data)
    else:
        return jsonify({"error": "Transaction not found"}), 404

@app.route('/blocks/<int:block_number>/transactions', methods=['GET'])
def get_block_transactions(block_number):
    # Query all transactions for the specified block number
    transactions = Transaction.query.filter_by(block_number=block_number).all()

    # Check if any transactions were found
    if transactions:
        # Prepare data for JSON serialization
        data = [
            {col.name: binary_to_hex(getattr(tx, col.name)) for col in Transaction.__table__.columns}
            for tx in transactions
        ]
        return jsonify(data)
    else:
        return jsonify({"error": "No transactions found for the specified block number"}), 404


import threading

def process_data(n, mode):
    if mode == 1:
        block_latest, block_lowest_fetched, block_highest_fetched = get_latest_blocks()
        if block_lowest_fetched is None or block_highest_fetched is None:
            fetch_and_store_transactions_in_block_range(block_from=(block_latest - n), block_to=block_latest)
        else:
            fetch_and_store_transactions_in_block_range(block_from=(block_lowest_fetched - n), block_to=(block_lowest_fetched - 1))
    elif mode == 2:
        df = read_from_db('SELECT DISTINCT transaction_hash FROM transactions WHERE transaction_hash NOT IN (SELECT transaction_hash FROM receipts)')
        for transaction_hash in df['transaction_hash']:
            try:
                fetch_and_process_receipts(transaction_hash)
            except Exception as e:
                logger.exception(e, transaction_hash)
    elif mode == 3:
        enrich()

@app.route('/process_data', methods=['POST'])
def process_data_endpoint():
    data = request.get_json()
    n = data.get('n', 10)  # default to 10 if not provided
    mode = data.get('mode', 3)  # default to mode 3 if not provided

    # Run the process in a background thread to avoid blocking
    thread = threading.Thread(target=process_data, args=(n, mode))
    thread.start()

    return jsonify({"status": "Process started"}), 202


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')