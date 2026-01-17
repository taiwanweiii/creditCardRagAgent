"""
LINE Bot integration for Credit Card Rewards RAG Agent
"""
from fastapi import FastAPI, Request, HTTPException, Header, Depends
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage
)
from typing import Optional
import re

from config import Config
from rag_engine import RAGEngine
from user_manager import UserManager
from vector_store import VectorStoreManager
from data_processor import CreditCardDataProcessor
from prompt_templates import WELCOME_MESSAGE, HELP_MESSAGE


class CreditCardLineBot:
    """LINE Bot for credit card recommendations"""
    
    def __init__(self):
        """Initialize LINE Bot"""
        self.app = FastAPI(title="Credit Card RAG Bot")
        
        # Initialize LINE Bot API
        if Config.LINE_CHANNEL_ACCESS_TOKEN and Config.LINE_CHANNEL_SECRET:
            self.line_bot_api = LineBotApi(Config.LINE_CHANNEL_ACCESS_TOKEN)
            self.handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)
        else:
            print("⚠️  LINE Bot credentials not configured")
            self.line_bot_api = None
            self.handler = None
        
        # Initialize RAG components
        self.user_manager = UserManager()
        self.vector_manager = VectorStoreManager()
        self.rag_engine: Optional[RAGEngine] = None
        self.card_processor: Optional[CreditCardDataProcessor] = None
        
        # Setup routes
        self._setup_routes()
        
        # Register handlers
        if self.handler:
            self._register_handlers()
    
    def initialize_rag(self):
        """Initialize RAG system"""
        print("🔄 Initializing RAG system...")
        
        # Initialize file manager
        from file_manager import CSVFileManager
        from pathlib import Path
        import tempfile
        
        file_manager = CSVFileManager(
            data_dir=Config.DATA_DIR,
            backup_dir=Config.BACKUP_DIR,
            max_backups=Config.MAX_BACKUPS
        )
        
        # Check if we have a CSV file
        latest_csv = file_manager.get_latest_csv()
        
        # If no CSV exists, try to download from Google Drive
        if not latest_csv:
            if Config.GOOGLE_DRIVE_ENABLED and Config.GOOGLE_DRIVE_FILE_ID:
                print("📥 No CSV found, downloading from Google Drive...")
                from google_drive_downloader import download_from_google_drive
                
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
                    print(f"✅ Downloaded and saved: {new_csv_path.name}")
                else:
                    print("❌ Failed to download from Google Drive")
                    print("⚠️  RAG system not initialized - please use /admin/refresh-vectordb API to initialize")
                    return
            else:
                print("⚠️  No CSV file found in data/ directory")
                print("⚠️  RAG system not initialized - please use /admin/refresh-vectordb API to initialize")
                print("💡 Tip: Enable Google Drive in .env or manually place a CSV file in data/")
                return
        
        # Get latest CSV path
        try:
            csv_path = Config.get_latest_csv_path()
        except FileNotFoundError:
            print("⚠️  RAG system not initialized - no CSV file available")
            return
        
        # Load credit card data
        self.card_processor = CreditCardDataProcessor(csv_path)
        documents = self.card_processor.prepare_documents()
        
        # Check for expired cards
        expired = self.card_processor.check_expired_cards()
        if expired:
            print(f"⚠️  Warning: {len(expired)} expired cards found")
        
        # Load or create vector store
        try:
            self.vector_manager.load_vectorstore()
            print("✅ Loaded existing vector store")
        except FileNotFoundError:
            print("📊 Creating new vector store...")
            self.vector_manager.create_vectorstore(documents)
        
        # Initialize RAG engine
        self.rag_engine = RAGEngine(self.vector_manager)
        print("✅ RAG system initialized")
    
    def _verify_admin_api_key(self, x_api_key: str = Header(None)):
        """Verify admin API key for protected endpoints"""
        if not Config.ADMIN_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Config 金鑰未設定"
            )
        
        if not x_api_key or x_api_key != Config.ADMIN_API_KEY:
            raise HTTPException(
                status_code=401,
                detail="金鑰驗證失敗"
            )
        
        return True
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "status": "running",
                "service": "Credit Card RAG Bot",
                "version": "1.0.0"
            }
        
        @self.app.get("/health")
        async def health_check():
            rag_ready = self.rag_engine is not None
            return {
                "status": "healthy",
                "rag_initialized": rag_ready,
                "message": "Ready" if rag_ready else "RAG not initialized - call /admin/refresh-vectordb to initialize",
                "users_count": self.user_manager.get_user_count()
            }
        
        @self.app.post("/webhook")
        async def webhook(request: Request):
            """LINE Bot webhook endpoint"""
            if not self.handler:
                raise HTTPException(status_code=500, detail="LINE Bot not configured")
            
            signature = request.headers.get('X-Line-Signature', '')
            body = await request.body()
            body = body.decode('utf-8')
            
            try:
                self.handler.handle(body, signature)
            except InvalidSignatureError:
                raise HTTPException(status_code=400, detail="Invalid signature")
            
            return {"status": "ok"}
        
        @self.app.post("/admin/refresh-vectordb")
        async def refresh_vectordb(authorized: bool = Depends(self._verify_admin_api_key)):
            """
            管理端點:更新向量資料庫
            需要在 Header 中提供 X-API-Key
            """
            try:
                print("\n" + "="*60)
                print("🔄 Admin API: Refreshing Vector Database")
                print("="*60)
                
                # Initialize file manager
                from file_manager import CSVFileManager
                from pathlib import Path
                import tempfile
                
                file_manager = CSVFileManager(
                    data_dir=Config.DATA_DIR,
                    backup_dir=Config.BACKUP_DIR,
                    max_backups=Config.MAX_BACKUPS
                )
                
                # Step 1: Check if Google Drive is enabled
                if not Config.GOOGLE_DRIVE_ENABLED or not Config.GOOGLE_DRIVE_FILE_ID:
                    print("\n❌ Step 1: Google Drive is required for updating vector database")
                    raise HTTPException(
                        status_code=400,
                        detail="更新向量資料庫需要啟用 Google Drive。請在 .env 設定 GOOGLE_DRIVE_ENABLED=True 和 GOOGLE_DRIVE_FILE_ID"
                    )
                
                # Step 2: Download from Google Drive
                from google_drive_downloader import download_from_google_drive
                
                print("\n📥 Step 2: Downloading from Google Drive...")
                
                # Download to temporary file first
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as tmp:
                    temp_csv_path = Path(tmp.name)
                
                success = download_from_google_drive(
                    file_id=Config.GOOGLE_DRIVE_FILE_ID,
                    destination=str(temp_csv_path)
                )
                
                if not success:
                    print("❌ Google Drive download failed")
                    raise Exception("Failed to download from Google Drive")
                
                print("✅ Downloaded latest data from Google Drive")
                
                # Step 3: Backup current CSV if exists
                print("\n💾 Step 3: Backing up current CSV...")
                backed_up = file_manager.backup_current_csv()
                if backed_up:
                    print(f"✅ Current CSV backed up to backups/")
                else:
                    print("ℹ️  No current CSV to backup (first time setup)")
                
                # Step 4: Save new CSV with timestamp
                print("\n💾 Step 4: Saving new CSV with timestamp...")
                new_csv_path = file_manager.save_new_csv(temp_csv_path)
                print(f"✅ Saved as: {new_csv_path.name}")
                
                # Clean up temp file
                try:
                    temp_csv_path.unlink()
                except:
                    pass
                
                # Step 5: Clean up old backups
                print("\n🗑️  Step 5: Cleaning up old backups...")
                file_manager.cleanup_old_backups()
                backup_count = file_manager.get_backup_count()
                print(f"✅ Backup count: {backup_count}")
                
                # Step 6: Reload credit card data
                print("\n📊 Step 6: Loading credit card data...")
                self.card_processor = CreditCardDataProcessor(str(new_csv_path))
                documents = self.card_processor.prepare_documents()
                print(f"✅ Loaded {len(documents)} documents")
                
                # Check for expired cards
                expired = self.card_processor.check_expired_cards()
                if expired:
                    print(f"⚠️  Found {len(expired)} expired cards")
                
                # Step 7: Delete existing vector store
                print("\n🗑️  Step 7: Deleting existing vector store...")
                try:
                    self.vector_manager.delete_collection()
                    print("✅ Deleted old vector store")
                except Exception as e:
                    print(f"⚠️  Error deleting old vector store: {e}")
                
                # Step 8: Create new vector store
                print("\n📊 Step 8: Creating new vector store...")
                self.vector_manager.create_vectorstore(documents)
                print("✅ Created new vector store")
                
                # Step 9: Reinitialize RAG engine
                print("\n🔄 Step 9: Reinitializing RAG engine...")
                self.rag_engine = RAGEngine(self.vector_manager)
                print("✅ RAG engine reinitialized")
                
                print("\n" + "="*60)
                print("✅ Vector database refresh complete!")
                print("="*60 + "\n")
                
                return {
                    "status": "success",
                    "message": "Vector database refreshed successfully",
                    "csv_filename": new_csv_path.name,
                    "documents_count": len(documents),
                    "expired_cards_count": len(expired) if expired else 0,
                    "backup_count": backup_count
                }
            
            except Exception as e:
                print(f"\n❌ Error refreshing vector database: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to refresh vector database: {str(e)}"
                )
        
        @self.app.get("/admin/status")
        async def admin_status(authorized: bool = Depends(self._verify_admin_api_key)):
            """
            管理端點:查詢系統詳細狀態
            需要在 Header 中提供 X-API-Key
            """
            try:
                # Get vector store stats
                vector_store_exists = False
                document_count = 0
                
                try:
                    if self.vector_manager.vectorstore:
                        vector_store_exists = True
                        # Try to get collection count
                        collection = self.vector_manager.vectorstore._collection
                        document_count = collection.count()
                except:
                    pass
                
                # Get expired cards
                expired_cards = []
                if self.card_processor:
                    expired_cards = self.card_processor.check_expired_cards()
                
                return {
                    "status": "healthy",
                    "rag_initialized": self.rag_engine is not None,
                    "vector_store_exists": vector_store_exists,
                    "documents_in_vectordb": document_count,
                    "users_count": self.user_manager.get_user_count(),
                    "expired_cards_count": len(expired_cards),
                    "expired_cards": expired_cards,
                    "google_drive_enabled": Config.GOOGLE_DRIVE_ENABLED,
                    "debug_mode": Config.DEBUG
                }
            
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get status: {str(e)}"
                )
    
    def _register_handlers(self):
        """Register LINE message handlers"""
        
        @self.handler.add(MessageEvent, message=TextMessage)
        def handle_text_message(event):
            """Handle text messages from LINE"""
            user_id = event.source.user_id
            text = event.message.text.strip()
            
            # Process message
            reply = self._process_message(user_id, text)
            
            # Send reply
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply)
            )
    
    def _process_message(self, user_id: str, text: str) -> str:
        """
        Process user message and generate reply
        
        Args:
            user_id: LINE user ID
            text: User's message
        
        Returns:
            Reply message
        """
        # Check if RAG is initialized
        if not self.rag_engine:
            return """⚠️ 系統尚未初始化

信用卡資料庫尚未建立，請聯繫管理員執行以下指令：

curl -X POST http://your-server/admin/refresh-vectordb -H "X-API-Key: your_key"

或等待系統管理員初始化資料庫。"""
        
        # Command: /start or /help
        if text.lower() in ['/start', '/help', '開始', '說明']:
            return WELCOME_MESSAGE if text.lower() == '/start' else HELP_MESSAGE
        
        # Command: /add [card_name]
        if text.startswith('/add '):
            card_name = text[5:].strip()
            return self._handle_add_card(user_id, card_name)
        
        # Command: /remove [card_name]
        if text.startswith('/remove '):
            card_name = text[8:].strip()
            return self._handle_remove_card(user_id, card_name)
        
        # Command: /list
        if text.lower() == '/list':
            return self._handle_list_cards(user_id)
        
        # Command: /clear
        if text.lower() == '/clear':
            return self._handle_clear_cards(user_id)
        
        # Query: Recommendation request
        return self._handle_query(user_id, text)
    
    def _handle_add_card(self, user_id: str, card_name: str) -> str:
        """Handle add card command"""
        # Validate card exists
        all_cards = self.card_processor.get_all_card_names()
        
        if card_name not in all_cards:
            # Try fuzzy matching
            matches = [c for c in all_cards if card_name in c or c in card_name]
            
            if matches:
                suggestions = "\n".join([f"• {c}" for c in matches[:5]])
                return f"❌ 找不到「{card_name}」\n\n💡 您是否要找:\n{suggestions}\n\n請使用完整的卡片名稱。"
            else:
                return f"❌ 找不到「{card_name}」\n\n請使用 /list 查看可用的信用卡清單。"
        
        # Add card
        success = self.user_manager.add_card(user_id, card_name)
        
        if success:
            card_count = self.user_manager.get_card_count(user_id)
            return f"✅ 已新增「{card_name}」\n\n您現在有 {card_count} 張信用卡。"
        else:
            return f"⚠️  您已經新增過「{card_name}」了!"
    
    def _handle_remove_card(self, user_id: str, card_name: str) -> str:
        """Handle remove card command"""
        success = self.user_manager.remove_card(user_id, card_name)
        
        if success:
            card_count = self.user_manager.get_card_count(user_id)
            return f"✅ 已移除「{card_name}」\n\n您現在有 {card_count} 張信用卡。"
        else:
            return f"❌ 您沒有「{card_name}」這張卡。"
    
    def _handle_list_cards(self, user_id: str) -> str:
        """Handle list cards command"""
        cards = self.user_manager.get_user_cards(user_id)
        
        if not cards:
            return "📋 您還沒有新增任何信用卡。\n\n使用 /add [卡片名稱] 來新增信用卡。"
        
        card_list = "\n".join([f"{i}. {card}" for i, card in enumerate(cards, 1)])
        return f"💳 您的信用卡 (共 {len(cards)} 張):\n\n{card_list}"
    
    def _handle_clear_cards(self, user_id: str) -> str:
        """Handle clear all cards command"""
        count = self.user_manager.clear_all_cards(user_id)
        
        if count > 0:
            return f"✅ 已清除 {count} 張信用卡。"
        else:
            return "📋 您沒有任何信用卡。"
    
    def _handle_query(self, user_id: str, query: str) -> str:
        """Handle recommendation query"""
        # Get user's cards
        user_cards = self.user_manager.get_user_cards(user_id)
        
        # Generate recommendation
        recommendation = self.rag_engine.recommend_cards(
            query=query,
            user_cards=user_cards,
            top_k=3
        )
        
        return recommendation
    
    def get_app(self) -> FastAPI:
        """Get FastAPI app instance"""
        return self.app


# Global bot instance
bot = CreditCardLineBot()


def get_bot() -> CreditCardLineBot:
    """Get bot instance"""
    return bot


if __name__ == "__main__":
    import uvicorn
    
    print("🤖 Starting Credit Card RAG Bot\n")
    
    # Initialize RAG system
    bot.initialize_rag()
    
    # Start server
    print(f"\n🚀 Server starting on {Config.HOST}:{Config.PORT}")
    print(f"📍 Webhook URL: http://{Config.HOST}:{Config.PORT}/webhook")
    
    uvicorn.run(
        bot.get_app(),
        host=Config.HOST,
        port=Config.PORT,
        log_level="info"
    )
