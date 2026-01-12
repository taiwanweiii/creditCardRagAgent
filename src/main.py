"""
Main entry point for Credit Card RAG Bot
"""
import uvicorn
from line_bot import get_bot
from config import Config


def main():
    """Main function to start the bot"""
    print("=" * 60)
    print("🤖 Credit Card Rewards RAG Agent")
    print("=" * 60)
    
    # Validate configuration
    try:
        Config.validate()
        print("✅ Configuration validated\n")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        return
    
    # Get bot instance
    bot = get_bot()
    
    # Initialize RAG system
    print("\n📊 Initializing RAG System...")
    print("-" * 60)
    bot.initialize_rag()
    
    # Start server
    print("\n🚀 Starting Server...")
    print("-" * 60)
    print(f"Host: {Config.HOST}")
    print(f"Port: {Config.PORT}")
    print(f"Webhook URL: http://{Config.HOST}:{Config.PORT}/webhook")
    print(f"Health Check: http://{Config.HOST}:{Config.PORT}/health")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(
        bot.get_app(),
        host=Config.HOST,
        port=Config.PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()
