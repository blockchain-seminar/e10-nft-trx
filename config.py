import os
from dotenv import load_dotenv
from utils import get_contract_abi

load_dotenv()

infura_api_key = os.environ['INFURA_API_KEY']
etherscan_api_key = os.environ['ETHSCAN_API_KEY']

# Define the contract_addresses to be fetched
contract_address = {
    "seaport_11": "0x00000000006c3852cbEf3e08E8dF289169EdE581",
    "seaport_12": "0x00000000000006c7676171937C444f6BDe3D6282",
    "seaport_13": "0x0000000000000aD24e80fd803C6ac37206a45f15",
    "seaport_14": "0x00000000000001ad428e4906aE43D8F9852d0dD6",
    "seaport_15": "0x00000000000000ADc04C56Bf30aC9d3c0aAF14dC",
    "seaport_16": "0x0000000000000068F116a894984e2DB1123eB395"
}

contract_abi = get_contract_abi(contract_address, etherscan_api_key)

