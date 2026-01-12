"""
測試 Gemini API 額度和連線狀態
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from config import Config

print("=" * 60)
print("🔍 Gemini API 狀態檢查")
print("=" * 60)

print(f"\n📋 API Key: {Config.GOOGLE_API_KEY[:20]}...")

try:
    # 建立 LLM
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        google_api_key=Config.GOOGLE_API_KEY,
        temperature=0.3
    )
    
    # 測試簡單查詢
    print(f"\n🔄 測試 API 呼叫...")
    messages = [HumanMessage(content="請回答: 測試")]
    
    response = llm.invoke(messages)
    
    print(f"✅ API 運作正常!")
    print(f"回應: {response.content[:100]}")
    
except Exception as e:
    error_msg = str(e)
    
    print(f"\n❌ API 呼叫失敗!")
    print(f"錯誤訊息: {error_msg[:200]}")
    
    # 分析錯誤類型
    if "quota" in error_msg.lower() or "429" in error_msg:
        print(f"\n⚠️  **額度問題**: API 免費額度已用盡")
        print(f"   解決方案:")
        print(f"   1. 等待明天額度重置")
        print(f"   2. 升級 API 方案")
        print(f"   3. 使用新的 API Key")
    elif "api" in error_msg.lower() and "key" in error_msg.lower():
        print(f"\n⚠️  **API Key 問題**: 請檢查 API Key 是否正確")
    elif "connection" in error_msg.lower():
        print(f"\n⚠️  **網路問題**: 請檢查網路連線")
    else:
        print(f"\n⚠️  **未知錯誤**: 請查看完整錯誤訊息")

print("\n" + "=" * 60)
