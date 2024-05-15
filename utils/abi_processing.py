import requests
import functools

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