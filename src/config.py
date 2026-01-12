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
    
    # Credit Card Data - 使用相對於專案根目錄的路徑
    CREDIT_CARD_CSV_PATH = os.getenv(
        "CREDIT_CARD_CSV_PATH", 
        str(PROJECT_ROOT / "信用卡資料模板.csv")
    )
    
    # Google Drive Integration
    GOOGLE_DRIVE_ENABLED = os.getenv("GOOGLE_DRIVE_ENABLED", "False").lower() == "true"
    GOOGLE_DRIVE_FILE_ID = os.getenv("GOOGLE_DRIVE_FILE_ID", "")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required")
        
        if not cls.LINE_CHANNEL_SECRET or not cls.LINE_CHANNEL_ACCESS_TOKEN:
            print("Warning: LINE Bot credentials not set. LINE Bot features will be disabled.")
        
        return True


# Validate configuration on import
if __name__ == "__main__":
    Config.validate()
    print("✅ Configuration validated successfully")
