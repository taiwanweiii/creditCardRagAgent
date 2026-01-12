"""
LINE Bot integration for Credit Card Rewards RAG Agent
"""
from fastapi import FastAPI, Request, HTTPException
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
        
        # Load credit card data
        self.card_processor = CreditCardDataProcessor(Config.CREDIT_CARD_CSV_PATH)
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
            return {
                "status": "healthy",
                "rag_initialized": self.rag_engine is not None,
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
            return "⚠️  系統初始化中,請稍後再試..."
        
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
