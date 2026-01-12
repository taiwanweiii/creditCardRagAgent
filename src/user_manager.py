"""
User management system for LINE Bot
Manages user data and their credit card collections
"""
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

from config import Config

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    line_user_id = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship
    cards = relationship("UserCard", back_populates="user", cascade="all, delete-orphan")


class UserCard(Base):
    """User's credit card model"""
    __tablename__ = 'user_cards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    card_name = Column(String, nullable=False)
    added_at = Column(DateTime, default=datetime.now)
    
    # Relationship
    user = relationship("User", back_populates="cards")


class UserManager:
    """Manage user data and credit cards"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize user manager
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url or Config.DATABASE_URL
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)
        
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def get_or_create_user(self, line_user_id: str) -> User:
        """
        Get existing user or create new one
        
        Args:
            line_user_id: LINE user ID
        
        Returns:
            User object
        """
        user = self.session.query(User).filter_by(line_user_id=line_user_id).first()
        
        if not user:
            user = User(line_user_id=line_user_id)
            self.session.add(user)
            self.session.commit()
            print(f"✅ Created new user: {line_user_id}")
        
        return user
    
    def add_card(self, line_user_id: str, card_name: str) -> bool:
        """
        Add credit card to user's collection
        
        Args:
            line_user_id: LINE user ID
            card_name: Credit card name
        
        Returns:
            True if added successfully, False if already exists
        """
        user = self.get_or_create_user(line_user_id)
        
        # Check if card already exists
        existing_card = self.session.query(UserCard).filter_by(
            user_id=user.id,
            card_name=card_name
        ).first()
        
        if existing_card:
            return False
        
        # Add new card
        new_card = UserCard(user_id=user.id, card_name=card_name)
        self.session.add(new_card)
        self.session.commit()
        
        print(f"✅ Added card '{card_name}' for user {line_user_id}")
        return True
    
    def remove_card(self, line_user_id: str, card_name: str) -> bool:
        """
        Remove credit card from user's collection
        
        Args:
            line_user_id: LINE user ID
            card_name: Credit card name
        
        Returns:
            True if removed successfully, False if not found
        """
        user = self.get_or_create_user(line_user_id)
        
        card = self.session.query(UserCard).filter_by(
            user_id=user.id,
            card_name=card_name
        ).first()
        
        if not card:
            return False
        
        self.session.delete(card)
        self.session.commit()
        
        print(f"✅ Removed card '{card_name}' for user {line_user_id}")
        return True
    
    def get_user_cards(self, line_user_id: str) -> List[str]:
        """
        Get all credit cards for a user
        
        Args:
            line_user_id: LINE user ID
        
        Returns:
            List of credit card names
        """
        user = self.get_or_create_user(line_user_id)
        
        cards = self.session.query(UserCard).filter_by(user_id=user.id).all()
        
        return [card.card_name for card in cards]
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        return self.session.query(User).count()
    
    def get_card_count(self, line_user_id: str) -> int:
        """Get number of cards for a user"""
        user = self.get_or_create_user(line_user_id)
        return self.session.query(UserCard).filter_by(user_id=user.id).count()
    
    def clear_all_cards(self, line_user_id: str) -> int:
        """
        Clear all cards for a user
        
        Args:
            line_user_id: LINE user ID
        
        Returns:
            Number of cards removed
        """
        user = self.get_or_create_user(line_user_id)
        
        count = self.session.query(UserCard).filter_by(user_id=user.id).count()
        self.session.query(UserCard).filter_by(user_id=user.id).delete()
        self.session.commit()
        
        print(f"✅ Cleared {count} cards for user {line_user_id}")
        return count
    
    def close(self):
        """Close database session"""
        self.session.close()


if __name__ == "__main__":
    # Test user manager
    print("👥 Testing User Manager\n")
    
    manager = UserManager()
    
    # Test user creation and card management
    test_user_id = "U1234567890"
    
    print(f"1. Adding cards for user {test_user_id}")
    manager.add_card(test_user_id, "台新Richart卡")
    manager.add_card(test_user_id, "國泰CUBE卡")
    manager.add_card(test_user_id, "中國信託LINE Pay卡")
    
    print(f"\n2. Getting user cards:")
    cards = manager.get_user_cards(test_user_id)
    print(f"   User has {len(cards)} cards: {cards}")
    
    print(f"\n3. Removing a card:")
    manager.remove_card(test_user_id, "國泰CUBE卡")
    cards = manager.get_user_cards(test_user_id)
    print(f"   User now has {len(cards)} cards: {cards}")
    
    print(f"\n4. Total users: {manager.get_user_count()}")
    
    manager.close()
