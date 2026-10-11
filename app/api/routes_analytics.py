from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models import Order, OrderItem, CustomerFeedback, MenuItem

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Insights"])

@router.get("/insights")
def get_insights(db: Session = Depends(get_db)):
    total_orders = db.query(Order).count()
    active_orders = db.query(Order).filter(Order.status.in_(["PLACED", "BREWING", "READY"])).count()
    completed_orders = db.query(Order).filter(Order.status == "COMPLETED").count()
    
    # Average rating
    avg_rating = db.query(func.avg(CustomerFeedback.rating)).scalar() or 5.0
    feedback_count = db.query(CustomerFeedback).count()

    # Recent feedback snippets
    recent_feedbacks = db.query(CustomerFeedback).order_by(CustomerFeedback.created_at.desc()).limit(5).all()

    # Top drinks ordered
    top_items = db.query(
        OrderItem.item_name,
        func.sum(OrderItem.quantity).label("total_sold")
    ).group_by(OrderItem.item_name).order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()

    return {
        "total_orders": total_orders,
        "active_orders": active_orders,
        "completed_orders": completed_orders,
        "average_rating": round(float(avg_rating), 1),
        "total_reviews": feedback_count,
        "top_drinks": [{"name": item[0], "sold": int(item[1])} for item in top_items],
        "recent_feedbacks": [f.to_dict() for f in recent_feedbacks]
    }
