"""
RAG Engine for credit card recommendation
"""
from typing import List, Optional, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

from config import Config
from vector_store import VectorStoreManager
from prompt_templates import (
    SYSTEM_PROMPT,
    QUERY_PROMPT_TEMPLATE,
    NO_CARDS_PROMPT
)


class RAGEngine:
    """RAG-based credit card recommendation engine"""
    
    def __init__(self, vector_store_manager: VectorStoreManager):
        """
        Initialize RAG engine
        
        Args:
            vector_store_manager: Vector store manager instance
        """
        self.vector_store = vector_store_manager
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash",
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.3,
            convert_system_message_to_human=True
        )
    
    def recommend_cards(
        self,
        query: str,
        user_cards: List[str],
        top_k: int = 3
    ) -> str:
        """
        Recommend credit cards based on user query
        
        Args:
            query: User's consumption scenario (e.g., "加油", "網購")
            user_cards: List of credit card names the user owns
            top_k: Number of recommendations to return
        
        Returns:
            Recommendation message
        """
        # Check if user has any cards
        if not user_cards:
            return self._format_no_cards_message()
        
        # Search for relevant cards from vector store
        search_results = self.vector_store.search(query, k=10)
        
        # Filter only user's cards
        user_card_docs = [
            doc for doc in search_results
            if doc.metadata['card_name'] in user_cards
        ]
        
        if not user_card_docs:
            return f"😅 您持有的信用卡中,沒有找到適合「{query}」的回饋方案。\n\n💡 建議您查看其他消費類型的回饋!"
        
        # Prepare context for LLM
        context = self._prepare_context(user_card_docs[:top_k * 2])
        user_cards_str = "\n".join([f"- {card}" for card in user_cards])
        
        # Detect category from query
        category = self._detect_category(query)
        
        # Create prompt
        prompt = QUERY_PROMPT_TEMPLATE.format(
            query=query,
            user_cards=user_cards_str,
            context=context,
            category=category
        )
        
        # Generate recommendation with error handling
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            error_msg = str(e)
            
            # 檢查是否為 API 額度問題
            if "quota" in error_msg.lower() or "429" in error_msg:
                return """❌ **Google Gemini API 額度已用盡**

很抱歉,目前無法生成推薦,因為 Google Gemini API 的免費額度已經用完了。

📊 **解決方案:**

1. **等待額度重置**
   - 免費額度每天會重置
   - 請明天再試

2. **升級 API 方案**
   - 前往 Google AI Studio 查看使用量
   - 網址: https://aistudio.google.com/app/apikey

3. **使用新的 API Key**
   - 建立新的 Google 帳號
   - 取得新的 API Key
   - 更新 .env 檔案

💡 **臨時方案:**
您仍然可以查看搜尋到的相關信用卡資訊,只是無法生成詳細的推薦說明。
"""
            
            # 檢查是否為網路問題
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                return """❌ **網路連線問題**

無法連接到 Google Gemini API,請檢查:

1. ✅ 網路連線是否正常
2. ✅ 防火牆是否阻擋 Python
3. ✅ 是否需要設定代理伺服器

請稍後再試!
"""
            
            # 檢查是否為 API Key 問題
            elif "api" in error_msg.lower() and "key" in error_msg.lower():
                return """❌ **API Key 設定問題**

Google Gemini API Key 可能有問題,請檢查:

1. ✅ .env 檔案中的 GOOGLE_API_KEY 是否正確
2. ✅ API Key 是否有效
3. ✅ API Key 是否已啟用 Gemini API

請前往 Google AI Studio 檢查您的 API Key。
網址: https://aistudio.google.com/app/apikey
"""
            
            # 其他錯誤
            else:
                return f"""❌ **發生錯誤**

生成推薦時發生問題:
{error_msg[:200]}

請稍後再試,或聯繫系統管理員。
"""
    
    def _prepare_context(self, documents: List) -> str:
        """Prepare context from retrieved documents"""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"""
【卡片 {i}】
{doc.page_content}
""".strip())
        
        return "\n\n".join(context_parts)
    
    def _detect_category(self, query: str) -> str:
        """Detect consumption category from query"""
        categories = {
            '加油': ['加油', '油錢', '中油', '台塑'],
            '網購': ['網購', '網路購物', '線上購物', 'momo', '蝦皮', 'pchome'],
            '餐廳': ['餐廳', '吃飯', '用餐', '美食', '餐飲'],
            '超商': ['超商', '便利商店', '7-11', '全家', 'ok', '萊爾富'],
            '旅遊': ['旅遊', '旅行', '出國', '機票', '飯店'],
            '影音': ['影音', 'netflix', 'disney', '串流', '訂閱'],
            '交通': ['交通', '高鐵', '台鐵', 'uber', '計程車', '捷運'],
        }
        
        query_lower = query.lower()
        
        for category, keywords in categories.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return '消費'
    
    def _format_no_cards_message(self) -> str:
        """Format message when user has no cards"""
        return NO_CARDS_PROMPT
    
    def get_card_details(self, card_name: str) -> Optional[str]:
        """
        Get detailed information about a specific card
        
        Args:
            card_name: Name of the credit card
        
        Returns:
            Card details or None if not found
        """
        results = self.vector_store.search(card_name, k=1)
        
        if not results:
            return None
        
        doc = results[0]
        if doc.metadata['card_name'] != card_name:
            return None
        
        return doc.page_content
    
    def analyze_all_user_cards(self, user_cards: List[str]) -> str:
        """
        Analyze all cards owned by user
        
        Args:
            user_cards: List of card names
        
        Returns:
            Analysis summary
        """
        if not user_cards:
            return "您還沒有新增任何信用卡。"
        
        summary_parts = [f"📊 您的信用卡分析 (共 {len(user_cards)} 張)\n"]
        
        for card_name in user_cards:
            details = self.get_card_details(card_name)
            if details:
                # Extract key info
                results = self.vector_store.search(card_name, k=1)
                if results:
                    metadata = results[0].metadata
                    summary_parts.append(f"""
💳 {card_name}
   銀行: {metadata['bank']}
   年費: {metadata['annual_fee']}元
   APP切換: {'需要' if metadata['requires_app_switch'] else '不需要'}
   到期日: {metadata['end_date']}
""".strip())
        
        return "\n\n".join(summary_parts)


if __name__ == "__main__":
    from data_processor import CreditCardDataProcessor
    
    print("🤖 Testing RAG Engine\n")
    
    # Initialize components
    processor = CreditCardDataProcessor("./信用卡資料模板.csv")
    documents = processor.prepare_documents()
    
    vector_manager = VectorStoreManager()
    
    # Try to load existing vector store, or create new one
    try:
        vector_manager.load_vectorstore()
    except FileNotFoundError:
        vector_manager.create_vectorstore(documents)
    
    # Create RAG engine
    rag_engine = RAGEngine(vector_manager)
    
    # Test recommendation
    print("🔍 測試查詢: 我要去加油\n")
    user_cards = ["中國信託中油聯名卡", "台新Richart卡", "滙豐匯鑽卡"]
    
    recommendation = rag_engine.recommend_cards(
        query="我要去加油",
        user_cards=user_cards
    )
    
    print(recommendation)
