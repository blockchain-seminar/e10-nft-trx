import os
from dotenv import load_dotenv
# from utils import get_contract_abi
from web3 import Web3

load_dotenv()

infura_api_key = os.environ['INFURA_API_KEY']
etherscan_api_key = os.environ['ETHSCAN_API_KEY']
url = os.environ['node']

#url = f'https://mainnet.infura.io/v3/{infura_api_key}'

w3 = Web3(Web3.HTTPProvider(url))