import random
import string
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import Order, OrderItem, MenuItem, CustomerFeedback

class OrderService:
    @staticmethod
    def generate_order_id() -> str:
        num = random.randint(1000, 9999)
        return f"SIP-{num}"

    @staticmethod
    def generate_pickup_code() -> str:
        return f"{random.randint(100, 999)}"

    @classmethod
    def calculate_estimated_wait_minutes(cls, db: Session) -> int:
        """
        Calculates wait time based on active queue size.
        Base wait: 3 minutes per order ahead in queue, minimum 4 minutes.
        """
        active_count = db.query(Order).filter(
            Order.status.in_(["PLACED", "BREWING"])
        ).count()
        return max(4, (active_count + 1) * 3)

    @classmethod
    def create_order(
        cls,
        db: Session,
        customer_name: str,
        session_id: str,
        items_data: List[Dict[str, Any]],
        customer_phone: Optional[str] = None,
        special_instructions: Optional[str] = None
    ) -> Order:
        order_id = cls.generate_order_id()
        pickup_code = cls.generate_pickup_code()
        wait_mins = cls.calculate_estimated_wait_minutes(db)

        total_amount = 0.0
        order_items = []

        for item_data in items_data:
            menu_item_id = item_data["menu_item_id"]
            quantity = max(1, int(item_data.get("quantity", 1)))
            customizations = item_data.get("customizations", {})

            menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
            if not menu_item:
                continue

            base_price = float(menu_item.price)
            # Extra shot adds $0.75
            extra_shots = int(customizations.get("extra_shots", 0))
            item_price = base_price + (extra_shots * 0.75)
            subtotal = item_price * quantity
            total_amount += subtotal

            order_item = OrderItem(
                order_id=order_id,
                menu_item_id=menu_item.id,
                item_name=menu_item.name,
                quantity=quantity,
                unit_price=item_price,
                subtotal=subtotal,
                customizations=customizations
            )
            order_items.append(order_item)

        order = Order(
            id=order_id,
            session_id=session_id,
            customer_name=customer_name.strip() or "Coffee Enthusiast",
            customer_phone=customer_phone,
            status="PLACED",
            total_amount=round(total_amount, 2),
            estimated_wait_minutes=wait_mins,
            pickup_code=pickup_code,
            special_instructions=special_instructions,
            items=order_items
        )

        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    @classmethod
    def get_order_with_queue_status(cls, db: Session, order_id: str) -> Optional[Dict[str, Any]]:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None

        # Calculate queue position
        if order.status in ["PLACED", "BREWING"]:
            orders_ahead = db.query(Order).filter(
                Order.status.in_(["PLACED", "BREWING"]),
                Order.created_at < order.created_at
            ).count()
            queue_position = orders_ahead + 1
        elif order.status == "READY":
            queue_position = 0
        else:
            queue_position = -1

        data = order.to_dict()
        data["queue_position"] = queue_position
        return data

    @classmethod
    def update_status(cls, db: Session, order_id: str, new_status: str) -> Optional[Order]:
        valid_statuses = ["PLACED", "BREWING", "READY", "COMPLETED", "CANCELLED"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")

        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None

        order.status = new_status
        order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(order)
        return order

    @classmethod
    def get_active_queue(cls, db: Session) -> List[Dict[str, Any]]:
        orders = db.query(Order).filter(
            Order.status.in_(["PLACED", "BREWING", "READY"])
        ).order_by(Order.created_at.asc()).all()
        return [order.to_dict() for order in orders]
