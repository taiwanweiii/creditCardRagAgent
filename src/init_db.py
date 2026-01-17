"""
Utility script to initialize vector database
Run this script to create/update the vector database from CSV
"""
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from data_processor import CreditCardDataProcessor
from vector_store import VectorStoreManager
from file_manager import CSVFileManager
from config import Config


def init_vector_db():
    """Initialize vector database from CSV"""
    print("=" * 60)
    print("📊 Vector Database Initialization")
    print("=" * 60)
    
    # Initialize file manager
    file_manager = CSVFileManager(
        data_dir=Config.DATA_DIR,
        backup_dir=Config.BACKUP_DIR,
        max_backups=Config.MAX_BACKUPS
    )
    
    # Download from Google Drive if enabled
    if Config.GOOGLE_DRIVE_ENABLED and Config.GOOGLE_DRIVE_FILE_ID:
        print(f"\n🌐 Google Drive 整合已啟用")
        from google_drive_downloader import download_from_google_drive
        
        # Backup current CSV if exists
        file_manager.backup_current_csv()
        
        # Download to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as tmp:
            temp_csv_path = Path(tmp.name)
        
        success = download_from_google_drive(
            file_id=Config.GOOGLE_DRIVE_FILE_ID,
            destination=str(temp_csv_path)
        )
        
        if success:
            # Save with timestamp
            new_csv_path = file_manager.save_new_csv(temp_csv_path)
            # Clean up temp file
            try:
                temp_csv_path.unlink()
            except:
                pass
            print(f"✅ 已從 Google Drive 更新資料: {new_csv_path.name}")
        else:
            print("❌ Google Drive 下載失敗")
            # Try to use existing CSV
            if not file_manager.get_latest_csv():
                raise FileNotFoundError(
                    "Google Drive 下載失敗且找不到本地 CSV 檔案。"
                    "請確認 Google Drive 設定是否正確。"
                )
            print("⚠️  使用現有的本地檔案")
    else:
        print("\n⚠️  Google Drive 未啟用，使用現有的本地檔案")
    
    # Get latest CSV path
    csv_path = Config.get_latest_csv_path()
    
    # Load credit card data
    print(f"\n1. Loading credit card data from: {csv_path}")
    processor = CreditCardDataProcessor(csv_path)
    documents = processor.prepare_documents()
    
    # Check for expired cards
    print("\n2. Checking for expired cards...")
    expired = processor.check_expired_cards()
    if expired:
        print(f"   ⚠️  Found {len(expired)} expired cards")
        for card in expired:
            print(f"      - {card}")
    else:
        print("   ✅ No expired cards found")
    
    # Create vector store
    print(f"\n3. Creating vector store at: {Config.CHROMA_PERSIST_DIRECTORY}")
    manager = VectorStoreManager()
    
    # Delete existing collection if exists
    try:
        manager.load_vectorstore()
        print("   🗑️  Deleting existing vector store...")
        manager.delete_collection()
    except FileNotFoundError:
        pass
    
    # Create new vector store
    manager.create_vectorstore(documents)
    
    # Test search
    print("\n4. Testing vector store...")
    test_queries = ["加油", "網購", "餐廳"]
    
    for query in test_queries:
        results = manager.search(query, k=3)
        print(f"\n   🔍 Query: '{query}'")
        for i, doc in enumerate(results, 1):
            print(f"      {i}. {doc.metadata['card_name']}")
    
    print("\n" + "=" * 60)
    print("✅ Vector database initialization complete!")
    print("=" * 60)


if __name__ == "__main__":
    init_vector_db()
