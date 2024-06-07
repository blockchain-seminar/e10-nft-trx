import pandas as pd
from config import w3
from utility_functions import get_contract_abi
from utility_functions.abi_processing import get_known_token_info
from utils import setup_logger
import json

logger = setup_logger()


def parse_abi_events(contract_address):
    ''' Used for parsing the fetched ABIs, results dumped in DB'''
    # Load the ABI from a JSON file
    with open(f'abi/{contract_address}.json', 'r') as file:
        abi_json = json.load(file)

    abi_events = [abi for abi in abi_json if abi["type"] == "event"]
    df = pd.DataFrame()
    id=0
    for event in abi_events:
        event['contract_address'] = contract_address
        event['id'] = id
        df_event = pd.DataFrame(event)
        try:
            for input in event['inputs']:
                input['id'] = id
                input = pd.DataFrame([input])
                input.columns = ['input_' + col for col in input.columns]
                merged_df = pd.merge(df_event, input, left_on='id', right_on='input_id', how='inner')
            merged_df.drop(columns=['inputs'], inplace=True)         
            df = pd.concat([df,merged_df])
        except:
            pass
        id += 1
    return merged_df


def determine_contract_type(log_address):
    """
    Basically, to check if it's NFT. Method supportsInterface should be called to check whether
    it supports 0x80ac58cd (ERC721) and 0xd9b67a26 (ERC1155).
    """
    erc721_interface_id = "0x80ac58cd"
    erc1155_interface_id = "0xd9b67a26"
    erc20_interface_id = "0x36372b07"
    #TODO what abi is that? do we need the custom abi?     token_contract = w3.eth.contract(address=log_address, abi=f'../abi/{log_address}.json')
    token_contract = w3.eth.contract(address=log_address, abi=[{
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
        is_erc20 = token_contract.functions.supportsInterface(erc20_interface_id).call()
        if is_erc721:
            return "ERC-721"
        elif is_erc1155:
            return "ERC-1155"
        elif is_erc20:
            return "ERC-20"
        else:
            return "Unknown"
    except Exception as e:
        logger.info(f'Not a 721 or 1155 contract, skipping: {e}')
        return "Unknown"


def parse_int_from_data(data):
    try:
        # Strip leading zeros and decode data to integer
        return int(data, 16)
    except ValueError as e:
        logger.info(f'Failed to parse:{data} with error {str(e)}')
        return None


# Get price data from block
def get_traded_price_and_currency(value_eth, topic, token_contract,data):
    traded_price = None
    currency = "ETH"

    # Check if transaction is in eth
    if value_eth > 0:
        traded_price = w3.from_wei(value_eth, 'ether')

    # If log represents an ERC-20 token transfer, get the token details
    if topic == w3.keccak(text="Transfer(address,address,uint256)").hex():
        if data is not None:
            token_value = parse_int_from_data(data)
        else:
            token_value = None

        known_token = get_known_token_info(token_contract)
        if known_token:
            symbol = known_token['symbol']
            decimals = known_token['decimals']
            traded_price = token_value / (10 ** decimals)
            currency = symbol
        else:
            try:
                erc20_abi = get_contract_abi(token_contract)
                token = w3.eth.contract(address=token_contract, abi=erc20_abi)
                erc20_abi_json = json.loads(erc20_abi)

                # Check if the contract has symbol and decimals functions
                if 'symbol' in [func['name'] for func in erc20_abi_json if 'name' in func]:
                    symbol = token.functions.symbol().call()
                else:
                    currency = None
                    raise Exception("symbol function not found in the contract")

                if 'decimals' in [func['name'] for func in erc20_abi_json if 'name' in func]:
                    decimals = token.functions.decimals().call()
                else:
                    currency = None
                    raise Exception("decimals function not found in the contract")

                traded_price = token_value / (10 ** decimals)
                currency = symbol
            except Exception as e:
                logger.exception(e)
                pass

    return traded_price, currency
