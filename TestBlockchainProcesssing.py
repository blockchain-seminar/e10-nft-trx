import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from data_processing import fetch_and_store_transactions_in_block_range, fetch_and_process_receipts, enrich
from main import main
class TestBlockchainProcessing(unittest.TestCase):
    @patch('main.setup_logger')
    @patch('main.get_latest_blocks')
    @patch('main.fetch_and_store_transactions_in_block_range')
    def test_main_mode_1(self, mock_fetch_and_store, mock_get_latest_blocks, mock_setup_logger):
        mock_setup_logger.return_value = unittest.mock.MagicMock()
        mock_get_latest_blocks.return_value = (100, 90, 100)
        main(mode=1)
        mock_fetch_and_store.assert_called_with(block_from=80, block_to=89)

    @patch('main.setup_logger')
    @patch('main.read_from_db')
    @patch('main.fetch_and_process_receipts')
    def test_main_mode_2_receipt_processing(self, mock_fetch_and_process_receipts, mock_read_from_db, mock_setup_logger):
        mock_logger = MagicMock()
        mock_setup_logger.return_value = mock_logger
        mock_read_from_db.return_value = {'transaction_hash': ['txhash1', 'txhash2', 'txhash3']}
        mock_fetch_and_process_receipts.side_effect = lambda x: None
        main(mode=2)
        mock_read_from_db.assert_called_once_with('select distinct transaction_hash from transactions where transaction_hash not in (select transaction_hash from receipts)')
        calls = [unittest.mock.call(tx_hash) for tx_hash in ['txhash1', 'txhash2', 'txhash3']]
        mock_fetch_and_process_receipts.assert_has_calls(calls, any_order=True)


    @patch('main.setup_logger')
    @patch('main.enrich')
    def test_main_mode_3_data_enrichment(self, mock_enrich, mock_setup_logger):
        mock_logger = MagicMock()
        mock_setup_logger.return_value = mock_logger
        main(mode=3)
        mock_enrich.assert_called_once()

    @patch('data_processing.logger')
    @patch('data_processing.w3.eth.get_block')
    @patch('data_processing.write_to_db')
    @patch('data_processing.filter_transactions_by_marketplace')
    def test_fetch_and_store_transactions_in_block_range(self, mock_filter_transactions, mock_write_to_db, mock_get_block, mock_logger):
        # Setup mock logging
        mock_logger.info = MagicMock()

        # Define the return value for the block data and transaction filtering
        transactions = [{'hash': '0x1', 'to': '0x123', 'from': '0x456'}]
        block_data = {'number': 1, 'transactions': transactions}
        mock_get_block.return_value = block_data

        # Ensure filter_transactions_by_marketplace returns a DataFrame with the expected structure, even if empty
        mock_filter_transactions.return_value = pd.DataFrame(transactions)

        # Execute function for a range of blocks
        block_from, block_to = 1, 2
        fetch_and_store_transactions_in_block_range(block_from, block_to)

        # Verify that write_to_db was called
        mock_write_to_db.assert_called()
        mock_filter_transactions.assert_called_with(transactions)

    @patch('data_processing.logger')
    @patch('data_processing.w3.eth.get_transaction_receipt')
    @patch('data_processing.process_and_store_receipts')
    def test_fetch_and_process_receipts(self, mock_process_and_store, mock_get_transaction_receipt, mock_logger):
        mock_logger.info = MagicMock()
        mock_get_transaction_receipt.return_value = MagicMock()
        fetch_and_process_receipts('0x123')
        mock_process_and_store.assert_called_once()

    @patch('data_processing.logger')
    @patch('data_processing.read_from_db')
    @patch('data_processing.write_to_db')
    @patch('data_processing.determine_contract_type')
    @patch('data_processing.get_traded_price_and_currency')
    def test_enrich(self, mock_get_traded_price_and_currency, mock_determine_contract_type, mock_write_to_db, mock_read_from_db, mock_logger):
        mock_logger.info = MagicMock()
        mock_get_traded_price_and_currency.return_value = (0, 'ETH')
        test_data = pd.DataFrame({
            'log_index': [1],
            'address': ['0xabc123'],
            'value': [100],
            'topics_0': ['0xdef456'],
            'topics_1': ['0x789abc'],
            'topics_2': ['0x123456'],
            'topics_3': ['0x654321'],
            'from_address': ['0xfromaddr'],
            'to_address': ['0xtoaddr'],
            'transaction_hash': ['0x987654321'],
            'data': ['0xdatacontent']
        })
        mock_read_from_db.return_value = test_data
        mock_determine_contract_type.return_value = "Unknown"

        enrich()

        mock_write_to_db.assert_called_once()
        mock_determine_contract_type.assert_called_with('0xabc123')
        mock_get_traded_price_and_currency.assert_called_once_with(100, '0xdef456', '0xabc123', '0xdatacontent')


if __name__ == '__main__':
    unittest.main()
