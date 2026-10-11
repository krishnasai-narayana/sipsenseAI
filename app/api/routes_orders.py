from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.db.session import get_db
from app.db.models import Order, CustomerFeedback
from app.services.order_service import OrderService
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/api/orders", tags=["Orders & Queue"])

class OrderItemInput(BaseModel):
    menu_item_id: int
    quantity: int = 1
    customizations: Dict[str, Any] = {}

class CreateOrderRequest(BaseModel):
    customer_name: str
    session_id: str
    items: List[OrderItemInput]
    customer_phone: Optional[str] = None
    special_instructions: Optional[str] = None

class StatusUpdateRequest(BaseModel):
    status: str

class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    taste_score: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

@router.post("")
def place_order(req: CreateOrderRequest, db: Session = Depends(get_db)):
    if not req.items:
        raise HTTPException(status_code=400, detail="Order must contain at least 1 drink")

    items_data = [item.model_dump() for item in req.items]
    order = OrderService.create_order(
        db=db,
        customer_name=req.customer_name,
        session_id=req.session_id,
        items_data=items_data,
        customer_phone=req.customer_phone,
        special_instructions=req.special_instructions
    )
    return OrderService.get_order_with_queue_status(db, order.id)

@router.get("/queue/live")
def get_live_queue(db: Session = Depends(get_db)):
    return OrderService.get_active_queue(db)

@router.get("/{order_id}")
def get_order_tracking(order_id: str, db: Session = Depends(get_db)):
    order_data = OrderService.get_order_with_queue_status(db, order_id)
    if not order_data:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_data

@router.post("/{order_id}/status")
def update_order_status(order_id: str, req: StatusUpdateRequest, db: Session = Depends(get_db)):
    try:
        updated = OrderService.update_status(db, order_id, req.status)
        if not updated:
            raise HTTPException(status_code=404, detail="Order not found")
        return OrderService.get_order_with_queue_status(db, order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/feedback")
def submit_feedback(order_id: str, req: FeedbackRequest, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    existing = db.query(CustomerFeedback).filter(CustomerFeedback.order_id == order_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Feedback already submitted for this order")

    # Generate AI sentiment insight using Gemini
    item_names = [item.item_name for item in order.items]
    ai_summary = gemini_service.summarize_feedback(req.rating, req.comment or "", item_names)

    feedback = CustomerFeedback(
        order_id=order_id,
        rating=req.rating,
        taste_score=req.taste_score,
        comment=req.comment,
        ai_sentiment_summary=ai_summary
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback.to_dict()
