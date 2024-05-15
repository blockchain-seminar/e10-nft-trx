from web3 import Web3

# Event signature hashes for ERC-721 and ERC-1155 Transfer events
erc721_transfer = Web3.keccak(text='Transfer(address,address,uint256)').hex()
erc1155_transfer_single = Web3.keccak(text='TransferSingle(address,address,address,uint256,uint256)').hex()
erc1155_transfer_batch = Web3.keccak(text='TransferBatch(address,address,address,uint256[],uint256[])').hex()

def determine_contract_type(log):
    if log['topics'][0].hex() == erc721_transfer:
        return 'ERC-721'
    elif log['topics'][0].hex() in [erc1155_transfer_single, erc1155_transfer_batch]:
        return 'ERC-1155'
    else:
        return 'Unknown'

def parse_int_from_data(data):
    try:
        # Strip leading zeros and decode data to integer
        return int(data.hex(), 16)
    except ValueError as e:
        print(f"Error parsing data: {data.hex()} with error {str(e)}")
        return 0



# Get price data from block
def get_traded_price_and_currency(tx_hash, log):
    traded_price = None
    currency = "ETH"

    # Check if transaction is in eth
    transaction = web3.eth.get_transaction(tx_hash)
    value_eth = transaction.value
    if value_eth > 0:
        traded_price = web3.from_wei(value_eth, 'ether')

    # If log represents an ERC-20 token transfer, get the token details
    if log['topics'][0].hex() == web3.keccak(text="Transfer(address,address,uint256)").hex():
        token_contract = log['address']
        token_value = parse_int_from_data(log['data']) if log['data'] else "Data Not Available"
        try:
            erc20_abi = get_contract_abi(token_contract)
            token = web3.eth.contract(address=token_contract, abi=erc20_abi)
            symbol = token.functions.symbol().call()
            decimals = token.functions.decimals().call()
            traded_price = token_value / (10 ** decimals)
            currency = symbol
        except Exception as e:
            print(f"Error processing ERC-20 transfer: {e}")
            currency= "Not Available"

    return traded_price, currency
