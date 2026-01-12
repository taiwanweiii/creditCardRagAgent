"""
Data processor for credit card information
Reads CSV file and prepares data for RAG system
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class CreditCardDataProcessor:
    """Process credit card data from CSV file"""
    
    def __init__(self, csv_path: str):
        """
        Initialize data processor
        
        Args:
            csv_path: Path to credit card CSV file
        """
        self.csv_path = Path(csv_path)
        self.df: Optional[pd.DataFrame] = None
        self.cards: List[Dict] = []
    
    def load_data(self) -> pd.DataFrame:
        """Load credit card data from CSV"""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        # Read CSV with proper encoding
        self.df = pd.read_csv(self.csv_path, encoding='utf-8-sig')
        
        # Validate required columns
        required_columns = [
            '信用卡名稱', '銀行', '回饋方案', 'APP切換方案',
            '回饋開始日', '回饋到期日', '年費', '備註'
        ]
        
        missing_columns = set(required_columns) - set(self.df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        print(f"✅ Loaded {len(self.df)} credit cards from CSV")
        return self.df
    
    def check_expired_cards(self) -> List[str]:
        """Check for expired credit card rewards"""
        if self.df is None:
            self.load_data()
        
        expired_cards = []
        today = datetime.now().date()
        
        for idx, row in self.df.iterrows():
            end_date_str = str(row['回饋到期日']).strip()
            
            # Skip if end date is "長期" or empty
            if end_date_str in ['長期', 'nan', '']:
                continue
            
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                if end_date < today:
                    expired_cards.append(row['信用卡名稱'])
            except ValueError:
                print(f"⚠️  Invalid date format for {row['信用卡名稱']}: {end_date_str}")
        
        if expired_cards:
            print(f"⚠️  Found {len(expired_cards)} expired cards: {expired_cards}")
        
        return expired_cards
    
    def prepare_documents(self) -> List[Dict]:
        """
        Prepare credit card data as documents for RAG
        
        Returns:
            List of dictionaries containing card info and metadata
        """
        if self.df is None:
            self.load_data()
        
        documents = []
        
        for idx, row in self.df.iterrows():
            # Create structured text content
            content = f"""
信用卡名稱: {row['信用卡名稱']}
發卡銀行: {row['銀行']}

回饋方案:
{row['回饋方案']}

APP切換說明:
{row['APP切換方案']}

年費: {row['年費']}元

備註: {row['備註']}

回饋期間: {row['回饋開始日']} 至 {row['回饋到期日']}
""".strip()
            
            # Create metadata
            metadata = {
                'card_name': row['信用卡名稱'],
                'bank': row['銀行'],
                'annual_fee': int(row['年費']) if pd.notna(row['年費']) else 0,
                'requires_app_switch': row['APP切換方案'] != '無需切換',
                'app_switch_info': row['APP切換方案'],
                'start_date': row['回饋開始日'],
                'end_date': row['回饋到期日'],
                'notes': row['備註']
            }
            
            documents.append({
                'content': content,
                'metadata': metadata
            })
        
        self.cards = documents
        print(f"✅ Prepared {len(documents)} documents for RAG")
        return documents
    
    def get_card_by_name(self, card_name: str) -> Optional[Dict]:
        """Get specific card information by name"""
        if not self.cards:
            self.prepare_documents()
        
        for card in self.cards:
            if card['metadata']['card_name'] == card_name:
                return card
        
        return None
    
    def get_all_card_names(self) -> List[str]:
        """Get list of all credit card names"""
        if self.df is None:
            self.load_data()
        
        return self.df['信用卡名稱'].tolist()


if __name__ == "__main__":
    # Test the data processor
    processor = CreditCardDataProcessor("./信用卡資料模板.csv")
    processor.load_data()
    processor.check_expired_cards()
    docs = processor.prepare_documents()
    
    print(f"\n📄 Sample document:")
    print(docs[0]['content'])
    print(f"\n📋 Metadata:")
    print(docs[0]['metadata'])
