"""
Command-line interface for testing RAG system without LINE Bot
測試用命令列介面 - 不需要 LINE Bot
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from data_processor import CreditCardDataProcessor
from vector_store import VectorStoreManager
from rag_engine import RAGEngine
from user_manager import UserManager
from config import Config
from prompt_templates import WELCOME_MESSAGE, HELP_MESSAGE


class TestCLI:
    """Command-line interface for testing"""
    
    def __init__(self):
        """Initialize test CLI"""
        self.user_id = "test_user"  # 測試用使用者 ID
        self.user_manager = UserManager()
        self.vector_manager = VectorStoreManager()
        self.rag_engine = None
        self.card_processor = None
        
        print("=" * 60)
        print("🤖 信用卡回饋 RAG Agent - 測試模式")
        print("=" * 60)
        
        self._initialize_rag()
    
    def _initialize_rag(self):
        """Initialize RAG system"""
        print("\n🔄 初始化 RAG 系統...")
        
        # Initialize file manager
        from file_manager import CSVFileManager
        
        file_manager = CSVFileManager(
            data_dir=Config.DATA_DIR,
            backup_dir=Config.BACKUP_DIR,
            max_backups=Config.MAX_BACKUPS
        )
        
        # Get latest CSV path
        csv_path = Config.get_latest_csv_path()
        
        # Load credit card data
        self.card_processor = CreditCardDataProcessor(csv_path)
        documents = self.card_processor.prepare_documents()
        
        # Check for expired cards
        expired = self.card_processor.check_expired_cards()
        if expired:
            print(f"⚠️  發現 {len(expired)} 張過期卡片")
        
        # Load or create vector store
        try:
            self.vector_manager.load_vectorstore()
            print("✅ 載入現有向量資料庫")
        except FileNotFoundError:
            print("📊 建立新的向量資料庫...")
            self.vector_manager.create_vectorstore(documents)
        
        # Initialize RAG engine
        self.rag_engine = RAGEngine(self.vector_manager)
        print("✅ RAG 系統初始化完成\n")
    
    def _process_command(self, text: str) -> str:
        """Process user command"""
        text = text.strip()
        
        # Command: help
        if text.lower() in ['help', '說明', 'h', '?']:
            return HELP_MESSAGE
        
        # Command: add [card_name]
        if text.startswith('add '):
            card_name = text[4:].strip()
            return self._handle_add_card(card_name)
        
        # Command: remove [card_name]
        if text.startswith('remove '):
            card_name = text[7:].strip()
            return self._handle_remove_card(card_name)
        
        # Command: list
        if text.lower() in ['list', '清單', 'l']:
            return self._handle_list_cards()
        
        # Command: clear
        if text.lower() in ['clear', '清除']:
            return self._handle_clear_cards()
        
        # Command: cards (顯示所有可用信用卡)
        if text.lower() in ['cards', '所有卡片', 'all']:
            return self._handle_show_all_cards()
        
        # Query: Recommendation request
        return self._handle_query(text)
    
    def _handle_add_card(self, card_name: str) -> str:
        """Handle add card command"""
        all_cards = self.card_processor.get_all_card_names()
        
        if card_name not in all_cards:
            # Try fuzzy matching
            matches = [c for c in all_cards if card_name in c or c in card_name]
            
            if matches:
                suggestions = "\n".join([f"  • {c}" for c in matches[:5]])
                return f"❌ 找不到「{card_name}」\n\n💡 您是否要找:\n{suggestions}\n\n請使用完整的卡片名稱。"
            else:
                return f"❌ 找不到「{card_name}」\n\n使用 'cards' 指令查看所有可用信用卡。"
        
        # Add card
        success = self.user_manager.add_card(self.user_id, card_name)
        
        if success:
            card_count = self.user_manager.get_card_count(self.user_id)
            return f"✅ 已新增「{card_name}」\n\n您現在有 {card_count} 張信用卡。"
        else:
            return f"⚠️  您已經新增過「{card_name}」了!"
    
    def _handle_remove_card(self, card_name: str) -> str:
        """Handle remove card command"""
        success = self.user_manager.remove_card(self.user_id, card_name)
        
        if success:
            card_count = self.user_manager.get_card_count(self.user_id)
            return f"✅ 已移除「{card_name}」\n\n您現在有 {card_count} 張信用卡。"
        else:
            return f"❌ 您沒有「{card_name}」這張卡。"
    
    def _handle_list_cards(self) -> str:
        """Handle list cards command"""
        cards = self.user_manager.get_user_cards(self.user_id)
        
        if not cards:
            return "📋 您還沒有新增任何信用卡。\n\n使用 'add [卡片名稱]' 來新增信用卡。"
        
        card_list = "\n".join([f"  {i}. {card}" for i, card in enumerate(cards, 1)])
        return f"💳 您的信用卡 (共 {len(cards)} 張):\n\n{card_list}"
    
    def _handle_clear_cards(self) -> str:
        """Handle clear all cards command"""
        count = self.user_manager.clear_all_cards(self.user_id)
        
        if count > 0:
            return f"✅ 已清除 {count} 張信用卡。"
        else:
            return "📋 您沒有任何信用卡。"
    
    def _handle_show_all_cards(self) -> str:
        """Show all available credit cards"""
        all_cards = self.card_processor.get_all_card_names()
        card_list = "\n".join([f"  {i}. {card}" for i, card in enumerate(all_cards, 1)])
        return f"💳 可用的信用卡清單 (共 {len(all_cards)} 張):\n\n{card_list}\n\n使用 'add [卡片名稱]' 來新增到您的清單。"
    
    def _handle_query(self, query: str) -> str:
        """Handle recommendation query"""
        user_cards = self.user_manager.get_user_cards(self.user_id)
        
        # Generate recommendation
        recommendation = self.rag_engine.recommend_cards(
            query=query,
            user_cards=user_cards,
            top_k=3
        )
        
        return recommendation
    
    def run(self):
        """Run interactive CLI"""
        print(WELCOME_MESSAGE)
        print("\n" + "=" * 60)
        print("💡 測試模式指令:")
        print("  • help          - 查看說明")
        print("  • cards         - 查看所有可用信用卡")
        print("  • add [卡片]    - 新增信用卡")
        print("  • remove [卡片] - 移除信用卡")
        print("  • list          - 查看已新增的卡片")
        print("  • clear         - 清除所有卡片")
        print("  • exit/quit     - 離開程式")
        print("  • 或直接輸入問題,例如: 我要去加油")
        print("=" * 60)
        
        while True:
            try:
                # Get user input
                user_input = input("\n💬 您: ").strip()
                
                # Check for exit
                if user_input.lower() in ['exit', 'quit', '離開', 'q']:
                    print("\n👋 再見!")
                    break
                
                if not user_input:
                    continue
                
                # Process command
                response = self._process_command(user_input)
                
                # Print response
                print(f"\n🤖 Bot:\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 再見!")
                break
            except Exception as e:
                print(f"\n❌ 錯誤: {e}")
        
        # Cleanup
        self.user_manager.close()


def main():
    """Main function"""
    try:
        cli = TestCLI()
        cli.run()
    except Exception as e:
        print(f"\n❌ 初始化失敗: {e}")
        print("\n請確認:")
        print("1. 已設定 GOOGLE_API_KEY 環境變數")
        print("2. 已執行 'python init_db.py' 初始化向量資料庫")
        print("3. CSV 檔案存在於 data/ 目錄")


if __name__ == "__main__":
    main()
