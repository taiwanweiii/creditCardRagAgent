"""
Utility script to initialize vector database
Run this script to create/update the vector database from CSV
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from data_processor import CreditCardDataProcessor
from vector_store import VectorStoreManager
from config import Config


def init_vector_db():
    """Initialize vector database from CSV"""
    print("=" * 60)
    print("📊 Vector Database Initialization")
    print("=" * 60)
    
    # Download from Google Drive if enabled
    if Config.GOOGLE_DRIVE_ENABLED:
        print(f"\n🌐 Google Drive 整合已啟用")
        if Config.GOOGLE_DRIVE_FILE_ID:
            from google_drive_downloader import download_from_google_drive
            
            success = download_from_google_drive(
                file_id=Config.GOOGLE_DRIVE_FILE_ID,
                destination=Config.CREDIT_CARD_CSV_PATH
            )
            
            if success:
                print("✅ 已從 Google Drive 更新資料")
            else:
                print("⚠️  Google Drive 下載失敗,使用本地檔案")
        else:
            print("⚠️  未設定 GOOGLE_DRIVE_FILE_ID,跳過下載")
    
    # Load credit card data
    print(f"\n1. Loading credit card data from: {Config.CREDIT_CARD_CSV_PATH}")
    processor = CreditCardDataProcessor(Config.CREDIT_CARD_CSV_PATH)
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
