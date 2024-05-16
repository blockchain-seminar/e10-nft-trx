import requests
import functools

from config import etherscan_api_key


# GET ABIs dynamicall for currency and price
@functools.lru_cache(maxsize=1000)  # Cache up to 1000 contract ABIs
def get_contract_abi(contract_address):
    url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={etherscan_api_key}"
    response = requests.get(url)
    response_json = response.json()

    if response_json['status'] == '1' and response_json['message'] == 'OK':
        contract_abi = response_json['result']
        return contract_abi
    else:
        raise Exception("Failed to fetch contract ABI: " + response_json.get('result', 'No additional error info'))

def get_known_token_info(token_contract):
    # Dictionary of known token contracts with their symbol and decimals
    known_tokens = {
        '0x0000000000A39bb272e79075ade125fd351887Ac': {'symbol': 'BLUR', 'decimals': 18}
        # Add other known tokens here
    }
    return known_tokens.get(token_contract)