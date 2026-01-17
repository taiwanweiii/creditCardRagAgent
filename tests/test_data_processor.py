"""
Test data processor functionality
"""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_processor import CreditCardDataProcessor
from config import Config


def get_csv_path():
    """Helper function to get the latest CSV path for testing"""
    return Config.get_latest_csv_path()


def test_load_data():
    """Test loading credit card data from CSV"""
    csv_path = get_csv_path()
    processor = CreditCardDataProcessor(csv_path)
    df = processor.load_data()
    
    assert df is not None
    assert len(df) > 0
    assert '信用卡名稱' in df.columns
    assert '銀行' in df.columns
    assert '回饋方案' in df.columns


def test_prepare_documents():
    """Test preparing documents for RAG"""
    csv_path = get_csv_path()
    processor = CreditCardDataProcessor(csv_path)
    documents = processor.prepare_documents()
    
    assert len(documents) > 0
    
    # Check document structure
    doc = documents[0]
    assert 'content' in doc
    assert 'metadata' in doc
    assert 'card_name' in doc['metadata']
    assert 'bank' in doc['metadata']


def test_get_card_by_name():
    """Test getting specific card by name"""
    csv_path = get_csv_path()
    processor = CreditCardDataProcessor(csv_path)
    processor.prepare_documents()
    
    # Get all card names first and test with the first one
    card_names = processor.get_all_card_names()
    assert len(card_names) > 0
    
    # Test get_card_by_name with the first card
    first_card_name = card_names[0]
    card = processor.get_card_by_name(first_card_name)
    assert card is not None
    assert card['metadata']['card_name'] == first_card_name


def test_get_all_card_names():
    """Test getting all card names"""
    csv_path = get_csv_path()
    processor = CreditCardDataProcessor(csv_path)
    card_names = processor.get_all_card_names()
    
    assert len(card_names) > 0
    # Verify all names are strings
    assert all(isinstance(name, str) for name in card_names)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
