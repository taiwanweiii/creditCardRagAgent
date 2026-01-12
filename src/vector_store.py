"""
Vector store management using ChromaDB and LangChain
"""
from typing import List, Dict, Optional
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from pathlib import Path

from config import Config


class VectorStoreManager:
    """Manage vector database for credit card information"""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize vector store manager
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory or Config.CHROMA_PERSIST_DIRECTORY
        
        # 使用本地免費的中文 embedding 模型
        print("🔄 Loading local embedding model (paraphrase-multilingual-MiniLM-L12-v2)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("✅ Embedding model loaded successfully")
        
        self.vectorstore: Optional[Chroma] = None
    
    def create_vectorstore(self, documents: List[Dict]) -> Chroma:
        """
        Create vector store from credit card documents
        
        Args:
            documents: List of document dictionaries with 'content' and 'metadata'
        
        Returns:
            ChromaDB vector store
        """
        # Convert to LangChain Document format
        langchain_docs = [
            Document(
                page_content=doc['content'],
                metadata=doc['metadata']
            )
            for doc in documents
        ]
        
        print(f"🔄 Creating vector store with {len(langchain_docs)} documents...")
        
        # Create ChromaDB vector store
        self.vectorstore = Chroma.from_documents(
            documents=langchain_docs,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="credit_cards"
        )
        
        print(f"✅ Vector store created and persisted to {self.persist_directory}")
        return self.vectorstore
    
    def load_vectorstore(self) -> Chroma:
        """
        Load existing vector store from disk
        
        Returns:
            ChromaDB vector store
        """
        persist_path = Path(self.persist_directory)
        
        if not persist_path.exists():
            raise FileNotFoundError(
                f"Vector store not found at {self.persist_directory}. "
                "Please create it first using create_vectorstore()"
            )
        
        print(f"🔄 Loading vector store from {self.persist_directory}...")
        
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name="credit_cards"
        )
        
        print(f"✅ Vector store loaded successfully")
        return self.vectorstore
    
    def search(self, query: str, k: int = 5, filter_dict: Optional[Dict] = None) -> List[Document]:
        """
        Search for relevant credit cards
        
        Args:
            query: Search query (e.g., "加油", "網購")
            k: Number of results to return
            filter_dict: Optional metadata filter
        
        Returns:
            List of relevant documents
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call load_vectorstore() first.")
        
        if filter_dict:
            results = self.vectorstore.similarity_search(
                query=query,
                k=k,
                filter=filter_dict
            )
        else:
            results = self.vectorstore.similarity_search(
                query=query,
                k=k
            )
        
        return results
    
    def search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        """
        Search with similarity scores
        
        Args:
            query: Search query
            k: Number of results
        
        Returns:
            List of (Document, score) tuples
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call load_vectorstore() first.")
        
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=k
        )
        
        return results
    
    def get_all_cards(self) -> List[Document]:
        """Get all credit cards from vector store"""
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call load_vectorstore() first.")
        
        # Get all documents by searching with a generic query
        return self.vectorstore.similarity_search("信用卡", k=100)
    
    def delete_collection(self):
        """Delete the vector store collection"""
        if self.vectorstore is None:
            print("⚠️  No vector store to delete")
            return
        
        self.vectorstore.delete_collection()
        print("✅ Vector store collection deleted")


if __name__ == "__main__":
    from data_processor import CreditCardDataProcessor
    
    # Test vector store creation
    print("📊 Testing Vector Store Manager\n")
    
    # Load credit card data
    processor = CreditCardDataProcessor("./信用卡資料模板.csv")
    documents = processor.prepare_documents()
    
    # Create vector store
    manager = VectorStoreManager()
    manager.create_vectorstore(documents)
    
    # Test search
    print("\n🔍 Testing search for '加油':")
    results = manager.search("加油", k=3)
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. {doc.metadata['card_name']}")
        print(f"   銀行: {doc.metadata['bank']}")
        print(f"   需要切換APP: {doc.metadata['requires_app_switch']}")
