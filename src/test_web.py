"""
Simple web interface for testing RAG system without LINE Bot
測試用網頁介面 - 不需要 LINE Bot
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from data_processor import CreditCardDataProcessor
from vector_store import VectorStoreManager
from rag_engine import RAGEngine
from user_manager import UserManager
from config import Config


app = FastAPI(title="Credit Card RAG Test Interface")

# Global instances
user_manager = UserManager()
vector_manager = VectorStoreManager()
rag_engine: Optional[RAGEngine] = None
card_processor: Optional[CreditCardDataProcessor] = None


class QueryRequest(BaseModel):
    """Query request model"""
    user_id: str = "test_user"
    message: str


class CardRequest(BaseModel):
    """Card management request model"""
    user_id: str = "test_user"
    card_name: str


@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    global rag_engine, card_processor
    
    print("🔄 Initializing RAG system...")
    
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
    card_processor = CreditCardDataProcessor(csv_path)
    documents = card_processor.prepare_documents()
    
    # Load or create vector store
    try:
        vector_manager.load_vectorstore()
        print("✅ Loaded existing vector store")
    except FileNotFoundError:
        print("📊 Creating new vector store...")
        vector_manager.create_vectorstore(documents)
    
    # Initialize RAG engine
    rag_engine = RAGEngine(vector_manager)
    print("✅ RAG system initialized")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve test web interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>信用卡回饋 RAG Agent - 測試介面</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 28px;
                margin-bottom: 10px;
            }
            
            .header p {
                opacity: 0.9;
                font-size: 14px;
            }
            
            .content {
                padding: 30px;
            }
            
            .section {
                margin-bottom: 30px;
            }
            
            .section h2 {
                color: #667eea;
                font-size: 20px;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .card-list {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                min-height: 60px;
            }
            
            .card-item {
                background: white;
                padding: 10px 15px;
                border-radius: 8px;
                margin-bottom: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .card-item:last-child {
                margin-bottom: 0;
            }
            
            .input-group {
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
            }
            
            input[type="text"] {
                flex: 1;
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            
            input[type="text"]:focus {
                outline: none;
                border-color: #667eea;
            }
            
            button {
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            button.secondary {
                background: #dc3545;
            }
            
            button.secondary:hover {
                box-shadow: 0 4px 12px rgba(220, 53, 69, 0.4);
            }
            
            .chat-container {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                min-height: 300px;
                max-height: 400px;
                overflow-y: auto;
                margin-bottom: 15px;
            }
            
            .message {
                margin-bottom: 15px;
                animation: fadeIn 0.3s;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .message.user {
                text-align: right;
            }
            
            .message-content {
                display: inline-block;
                padding: 12px 16px;
                border-radius: 12px;
                max-width: 80%;
                word-wrap: break-word;
                white-space: pre-wrap;
            }
            
            .message.user .message-content {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .message.bot .message-content {
                background: white;
                color: #333;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .empty-state {
                text-align: center;
                color: #999;
                padding: 20px;
            }
            
            .quick-actions {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 10px;
            }
            
            .quick-action {
                padding: 8px 16px;
                background: white;
                border: 2px solid #667eea;
                color: #667eea;
                border-radius: 20px;
                cursor: pointer;
                font-size: 13px;
                transition: all 0.2s;
            }
            
            .quick-action:hover {
                background: #667eea;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 信用卡回饋 RAG Agent</h1>
                <p>測試介面 - 不需要 LINE Bot</p>
            </div>
            
            <div class="content">
                <!-- 卡片管理 -->
                <div class="section">
                    <h2>💳 我的信用卡</h2>
                    <div id="cardList" class="card-list">
                        <div class="empty-state">尚未新增信用卡</div>
                    </div>
                    <div class="input-group">
                        <input type="text" id="cardInput" placeholder="輸入信用卡名稱,例如: 台新Richart卡">
                        <button onclick="addCard()">新增</button>
                        <button onclick="showAllCards()">查看所有卡片</button>
                    </div>
                </div>
                
                <!-- 對話區域 -->
                <div class="section">
                    <h2>💬 查詢推薦</h2>
                    <div id="chatContainer" class="chat-container">
                        <div class="empty-state">開始提問吧!例如: 我要去加油</div>
                    </div>
                    <div class="input-group">
                        <input type="text" id="queryInput" placeholder="輸入您的問題..." onkeypress="handleKeyPress(event)">
                        <button onclick="sendQuery()">查詢</button>
                    </div>
                    <div class="quick-actions">
                        <div class="quick-action" onclick="quickQuery('我要去加油')">🚗 加油</div>
                        <div class="quick-action" onclick="quickQuery('網購要用哪張卡')">🛒 網購</div>
                        <div class="quick-action" onclick="quickQuery('餐廳吃飯推薦')">🍽️ 餐廳</div>
                        <div class="quick-action" onclick="quickQuery('超商消費')">🏪 超商</div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const userId = 'test_user';
            
            // Load user cards on page load
            window.onload = function() {
                loadUserCards();
            };
            
            async function loadUserCards() {
                try {
                    const response = await fetch(`/api/cards?user_id=${userId}`);
                    const data = await response.json();
                    displayCards(data.cards);
                } catch (error) {
                    console.error('Error loading cards:', error);
                }
            }
            
            function displayCards(cards) {
                const cardList = document.getElementById('cardList');
                
                if (cards.length === 0) {
                    cardList.innerHTML = '<div class="empty-state">尚未新增信用卡</div>';
                    return;
                }
                
                cardList.innerHTML = cards.map(card => `
                    <div class="card-item">
                        <span>${card}</span>
                        <button class="secondary" onclick="removeCard('${card}')">移除</button>
                    </div>
                `).join('');
            }
            
            async function addCard() {
                const input = document.getElementById('cardInput');
                const cardName = input.value.trim();
                
                if (!cardName) {
                    alert('請輸入信用卡名稱');
                    return;
                }
                
                try {
                    const response = await fetch('/api/cards/add', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_id: userId, card_name: cardName })
                    });
                    
                    const data = await response.json();
                    alert(data.message);
                    
                    if (data.success) {
                        input.value = '';
                        loadUserCards();
                    }
                } catch (error) {
                    alert('新增失敗: ' + error);
                }
            }
            
            async function removeCard(cardName) {
                if (!confirm(`確定要移除「${cardName}」嗎?`)) {
                    return;
                }
                
                try {
                    const response = await fetch('/api/cards/remove', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_id: userId, card_name: cardName })
                    });
                    
                    const data = await response.json();
                    alert(data.message);
                    loadUserCards();
                } catch (error) {
                    alert('移除失敗: ' + error);
                }
            }
            
            async function showAllCards() {
                try {
                    const response = await fetch('/api/cards/all');
                    const data = await response.json();
                    alert('可用的信用卡:\\n\\n' + data.cards.join('\\n'));
                } catch (error) {
                    alert('查詢失敗: ' + error);
                }
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendQuery();
                }
            }
            
            function quickQuery(query) {
                document.getElementById('queryInput').value = query;
                sendQuery();
            }
            
            async function sendQuery() {
                const input = document.getElementById('queryInput');
                const query = input.value.trim();
                
                if (!query) {
                    return;
                }
                
                // Add user message to chat
                addMessage(query, 'user');
                input.value = '';
                
                try {
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_id: userId, message: query })
                    });
                    
                    const data = await response.json();
                    addMessage(data.response, 'bot');
                } catch (error) {
                    addMessage('查詢失敗: ' + error, 'bot');
                }
            }
            
            function addMessage(content, type) {
                const chatContainer = document.getElementById('chatContainer');
                
                // Remove empty state if exists
                const emptyState = chatContainer.querySelector('.empty-state');
                if (emptyState) {
                    emptyState.remove();
                }
                
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
                
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/cards")
async def get_user_cards(user_id: str = "test_user"):
    """Get user's credit cards"""
    cards = user_manager.get_user_cards(user_id)
    return {"cards": cards}


@app.get("/api/cards/all")
async def get_all_cards():
    """Get all available credit cards"""
    all_cards = card_processor.get_all_card_names()
    return {"cards": all_cards}


@app.post("/api/cards/add")
async def add_card(request: CardRequest):
    """Add credit card to user's collection"""
    all_cards = card_processor.get_all_card_names()
    
    if request.card_name not in all_cards:
        return {
            "success": False,
            "message": f"找不到「{request.card_name}」,請使用完整的卡片名稱"
        }
    
    success = user_manager.add_card(request.user_id, request.card_name)
    
    if success:
        card_count = user_manager.get_card_count(request.user_id)
        return {
            "success": True,
            "message": f"✅ 已新增「{request.card_name}」\n您現在有 {card_count} 張信用卡"
        }
    else:
        return {
            "success": False,
            "message": f"您已經新增過「{request.card_name}」了"
        }


@app.post("/api/cards/remove")
async def remove_card(request: CardRequest):
    """Remove credit card from user's collection"""
    success = user_manager.remove_card(request.user_id, request.card_name)
    
    if success:
        card_count = user_manager.get_card_count(request.user_id)
        return {
            "success": True,
            "message": f"✅ 已移除「{request.card_name}」\n您現在有 {card_count} 張信用卡"
        }
    else:
        return {
            "success": False,
            "message": f"您沒有「{request.card_name}」這張卡"
        }


@app.post("/api/query")
async def query_recommendation(request: QueryRequest):
    """Query credit card recommendation"""
    user_cards = user_manager.get_user_cards(request.user_id)
    
    # Generate recommendation
    recommendation = rag_engine.recommend_cards(
        query=request.message,
        user_cards=user_cards,
        top_k=3
    )
    
    return {"response": recommendation}


if __name__ == "__main__":
    import uvicorn
    
    print("🌐 Starting Web Test Interface...")
    print(f"📍 Open browser: http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
