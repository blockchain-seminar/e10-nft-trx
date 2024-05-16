from config import web3
from utility_functions import get_contract_abi
from utils import setup_logger

logger = setup_logger()
def determine_contract_type(log):
    """
    Thanks, identified how to it earlier, but forgot to write the answer.
    Basically, to check if it's NFT. Method supportsInterface should be called to check whether
    it supports 0x80ac58cd (ERC721) and 0xd9b67a26 (ERC1155).
    """
    erc721_interface_id = "0x80ac58cd"
    erc1155_interface_id = "0xd9b67a26"
    token_contract = web3.eth.contract(address=log['address'], abi=[{
        "constant": True,
        "inputs": [{"name": "interfaceID", "type": "bytes4"}],
        "name": "supportsInterface",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }])

    try:
        # Querying the contract to see if it supports the ERC-721 interface
        is_erc1155 = token_contract.functions.supportsInterface(erc1155_interface_id).call()
        is_erc721 = token_contract.functions.supportsInterface(erc721_interface_id).call()
        if is_erc721:
            return "ERC-721"
        elif is_erc1155:
            return "ERC-1155"
        else:
            return "Unknown"
    except Exception as e:
        logger.info(f'Not a 721 or 1155 contract, skipping: {e}')
        return "Unknown"



def parse_int_from_data(data):
    try:
        # Strip leading zeros and decode data to integer
        return int(data.hex(), 16)
    except ValueError as e:
        logger.info(f'Failed to parse:{data.hex()} with error {str(e)}')
        return 0



# Get price data from block
def get_traded_price_and_currency(transaction, log):
    traded_price = None
    currency = "ETH"

    # Check if transaction is in eth
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
            currency = "Not Available"

    return traded_price, currency
