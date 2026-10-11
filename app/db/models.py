from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean,
    DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.db.session import Base

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True)
    category = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    roast_level = Column(String(30), default="Medium")
    sweetness_level = Column(Integer, default=1)  # 0 to 5 scale
    intensity = Column(Integer, default=3)        # 1 to 5 scale
    caffeine_level = Column(String(30), default="Medium")
    flavor_notes = Column(JSON, default=list)     # ["Hazelnut", "Citrus", "Honey"]
    milk_options = Column(JSON, default=list)     # ["Whole Milk", "Oat Milk", "Almond Milk", "None"]
    temperature_default = Column(String(20), default="Hot") # "Hot" or "Iced"
    image_url = Column(String(500), nullable=True)
    is_available = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    calories = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "price": float(self.price),
            "roast_level": self.roast_level,
            "sweetness_level": self.sweetness_level,
            "intensity": self.intensity,
            "caffeine_level": self.caffeine_level,
            "flavor_notes": self.flavor_notes or [],
            "milk_options": self.milk_options or [],
            "temperature_default": self.temperature_default,
            "image_url": self.image_url,
            "is_available": self.is_available,
            "is_featured": self.is_featured,
            "calories": self.calories,
        }

class CustomerPreference(Base):
    __tablename__ = "customer_preferences"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    customer_name = Column(String(100), nullable=True)
    preferred_roast = Column(String(30), nullable=True)
    sweetness_pref = Column(Integer, default=2)
    milk_pref = Column(String(50), nullable=True)
    temperature_pref = Column(String(20), default="Iced")
    caffeine_pref = Column(String(30), default="Medium")
    favorite_flavors = Column(JSON, default=list)
    dietary_notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"

    id = Column(String(50), primary_key=True, index=True)  # e.g., "SIP-8823"
    session_id = Column(String(100), index=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(30), nullable=True)
    status = Column(String(30), default="PLACED", index=True)  # PLACED, BREWING, READY, COMPLETED, CANCELLED
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.0)
    estimated_wait_minutes = Column(Integer, default=5)
    pickup_code = Column(String(10), nullable=False)
    special_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    feedback = relationship("CustomerFeedback", back_populates="order", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "status": self.status,
            "total_amount": float(self.total_amount),
            "estimated_wait_minutes": self.estimated_wait_minutes,
            "pickup_code": self.pickup_code,
            "special_instructions": self.special_instructions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "items": [item.to_dict() for item in self.items],
            "has_feedback": self.feedback is not None
        }

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    item_name = Column(String(150), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    customizations = Column(JSON, default=dict)  # {"milk": "Oat", "sweetness": "Light", "shots": 1, "ice": "Regular"}

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")

    def to_dict(self):
        return {
            "id": self.id,
            "menu_item_id": self.menu_item_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "subtotal": float(self.subtotal),
            "customizations": self.customizations or {}
        }

class CustomerFeedback(Base):
    __tablename__ = "customer_feedback"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    rating = Column(Integer, nullable=False)  # 1 to 5
    taste_score = Column(Integer, nullable=True) # 1 to 5
    comment = Column(Text, nullable=True)
    ai_sentiment_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="feedback")

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "rating": self.rating,
            "taste_score": self.taste_score,
            "comment": self.comment,
            "ai_sentiment_summary": self.ai_sentiment_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
