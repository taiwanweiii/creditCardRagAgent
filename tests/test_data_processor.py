"""
Test data processor functionality
"""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_processor import CreditCardDataProcessor


def test_load_data():
    """Test loading credit card data from CSV"""
    processor = CreditCardDataProcessor("./信用卡資料模板.csv")
    df = processor.load_data()
    
    assert df is not None
    assert len(df) > 0
    assert '信用卡名稱' in df.columns
    assert '銀行' in df.columns
    assert '回饋方案' in df.columns


def test_prepare_documents():
    """Test preparing documents for RAG"""
    processor = CreditCardDataProcessor("./信用卡資料模板.csv")
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
    processor = CreditCardDataProcessor("./信用卡資料模板.csv")
    processor.prepare_documents()
    
    card = processor.get_card_by_name("台新Richart卡")
    assert card is not None
    assert card['metadata']['card_name'] == "台新Richart卡"


def test_get_all_card_names():
    """Test getting all card names"""
    processor = CreditCardDataProcessor("./信用卡資料模板.csv")
    card_names = processor.get_all_card_names()
    
    assert len(card_names) > 0
    assert "台新Richart卡" in card_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
