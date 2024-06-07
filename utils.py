import os, json
import logging
import requests

from config import etherscan_api_key


def setup_logger():
    logger = logging.getLogger('Logging')
    if not logger.handlers:  # Check if handlers are already set
        logger.setLevel(logging.DEBUG)
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler('app.log')
        c_handler.setLevel(logging.WARNING)
        f_handler.setLevel(logging.DEBUG)
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
    return logger

def find_key_by_value(d, target_value):
    for key, value in d.items():
        if value == target_value:
            return key
    return None  

def read_json_to_dict(directory):
    data = {}
    # Loop through every file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.json'):  # Check if the file is a JSON file
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                # Remove the '.json' suffix from the filename before using it as a key
                key = os.path.splitext(filename)[0]
                # Load JSON data and store it in the dictionary with filename as key
                data[key] = json.load(file)
    return data

def fetch_contract_abi(contract_address):
    """
    Fetches the ABI (Application Binary Interface) for a given contract address from the Etherscan API, utilizing caching to optimize performance. Raises an exception if the ABI cannot be retrieved.
    """
    print('get contract abi start')
    print('fetching the abi for a given contract address from the etherscan api')
    print('currently fetching for : ')
    print(contract_address)
    url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={etherscan_api_key}"
    response = requests.get(url)
    response_json = response.json()

    if response_json['status'] == '1' and response_json['message'] == 'OK':
        contract_abi = response_json['result']
        print('get contract abi end')
        return contract_abi
    else:
        raise Exception("Failed to fetch contract ABI: " + response_json.get('result', 'No additional error info'))

def get_contract_abi(marketplaces):
    contract_abi = read_json_to_dict('abi')
    for address in marketplaces['contract_address']:
        try:
            if contract_abi.get(address) is None:
                abi = fetch_contract_abi(address)
                with open(f'abi/{address}.json', 'w', encoding='utf-8') as file:
                    file.write(abi)
        except:
            pass
    contract_abi = read_json_to_dict('abi')
    return contract_abi
