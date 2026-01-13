"""
Configuration management for Credit Card Rewards RAG Agent
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 取得專案根目錄 (config.py 的父目錄的父目錄)
PROJECT_ROOT = Path(__file__).parent.parent


class Config:
    """Application configuration"""
    
    # Google Gemini API
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    
    # LINE Bot Configuration
    LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./creditcard.db")
    
    # Application Settings
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    
    # CSV File Management
    DATA_DIR = os.getenv("DATA_DIR", str(PROJECT_ROOT / "data"))
    BACKUP_DIR = os.getenv("BACKUP_DIR", str(PROJECT_ROOT / "backups"))
    MAX_BACKUPS = int(os.getenv("MAX_BACKUPS", "30"))
    
    # Credit Card Data - 動態取得最新的 CSV 檔案
    # 注意:實際路徑由 file_manager 動態決定
    CREDIT_CARD_CSV_PATH = os.getenv(
        "CREDIT_CARD_CSV_PATH", 
        str(PROJECT_ROOT / "信用卡資料模板.csv")  # 向後相容的預設值
    )
    
    # Google Drive Integration
    GOOGLE_DRIVE_ENABLED = os.getenv("GOOGLE_DRIVE_ENABLED", "False").lower() == "true"
    GOOGLE_DRIVE_FILE_ID = os.getenv("GOOGLE_DRIVE_FILE_ID", "")
    
    # Admin API
    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")
    
    @classmethod
    def get_latest_csv_path(cls):
        """Get path to the latest CSV file in data directory"""
        from file_manager import CSVFileManager
        
        manager = CSVFileManager(
            data_dir=cls.DATA_DIR,
            backup_dir=cls.BACKUP_DIR,
            max_backups=cls.MAX_BACKUPS
        )
        
        latest_csv = manager.get_latest_csv()
        
        if latest_csv:
            return str(latest_csv)
        
        # Fallback to legacy path for backward compatibility
        return cls.CREDIT_CARD_CSV_PATH
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required")
        
        if not cls.LINE_CHANNEL_SECRET or not cls.LINE_CHANNEL_ACCESS_TOKEN:
            print("Warning: LINE Bot credentials not set. LINE Bot features will be disabled.")
        
        if not cls.DEBUG and not cls.ADMIN_API_KEY:
            raise ValueError("ADMIN_API_KEY is required in production mode")
        
        return True


# Validate configuration on import
if __name__ == "__main__":
    Config.validate()
    print("✅ Configuration validated successfully")
