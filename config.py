import os
from dotenv import load_dotenv
# from utils import get_contract_abi
from web3 import Web3

load_dotenv()

infura_api_key = os.environ['INFURA_API_KEY']
etherscan_api_key = os.environ['ETHSCAN_API_KEY']

#url = f'https://mainnet.infura.io/v3/{infura_api_key}'
url = 'http://127.0.0.1:8547'
w3 = Web3(Web3.HTTPProvider(url))