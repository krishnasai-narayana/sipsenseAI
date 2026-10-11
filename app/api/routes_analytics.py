from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from app.db.session import get_db
from app.db.models import Order, OrderItem, CustomerFeedback, MenuItem

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Insights"])

@router.get("/insights")
def get_insights(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    total_orders = len(orders)
    active_orders = len([o for o in orders if o.status in ["PLACED", "BREWING", "READY"]])
    completed_orders = len([o for o in orders if o.status == "COMPLETED"])
    
    # Financial metrics
    total_revenue = sum([float(o.total_amount) for o in orders])
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0

    today = date.today()
    today_orders_list = [o for o in orders if o.created_at and o.created_at.date() == today]
    today_revenue = sum([float(o.total_amount) for o in today_orders_list])
    today_orders_count = len(today_orders_list)

    # Customer Feedback & Ratings
    feedbacks = db.query(CustomerFeedback).all()
    feedback_count = len(feedbacks)
    avg_rating = (sum([f.rating for f in feedbacks]) / feedback_count) if feedback_count > 0 else 5.0

    rating_histogram = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for f in feedbacks:
        if f.rating in rating_histogram:
            rating_histogram[f.rating] += 1
    
    positive_reviews = rating_histogram[4] + rating_histogram[5]
    positive_sentiment_pct = (positive_reviews / feedback_count * 100) if feedback_count > 0 else 100.0

    # Recent feedback snippets
    recent_feedbacks = db.query(CustomerFeedback).order_by(CustomerFeedback.created_at.desc()).limit(6).all()

    # Order Items Analysis
    order_items = db.query(OrderItem).all()
    
    # Top drinks ordered
    drink_sales = {}
    milk_dist = {"Oat Milk": 0, "Whole Milk": 0, "Almond Milk": 0, "Black / None": 0}
    temp_dist = {"Hot": 0, "Iced": 0}
    sweetness_dist = {"0 (Unsweet)": 0, "1 (Subtle)": 0, "2 (Balanced)": 0, "3+ (Sweet)": 0}

    for item in order_items:
        # Drink count
        drink_sales[item.item_name] = drink_sales.get(item.item_name, 0) + item.quantity
        
        # Milk preferences
        cust = item.customizations or {}
        milk = cust.get("milk", "Whole Milk")
        if "oat" in milk.lower():
            milk_dist["Oat Milk"] += item.quantity
        elif "almond" in milk.lower():
            milk_dist["Almond Milk"] += item.quantity
        elif "none" in milk.lower() or "black" in milk.lower():
            milk_dist["Black / None"] += item.quantity
        else:
            milk_dist["Whole Milk"] += item.quantity

        # Temp preferences
        temp = cust.get("temperature", "Hot")
        if "ice" in temp.lower():
            temp_dist["Iced"] += item.quantity
        else:
            temp_dist["Hot"] += item.quantity

        # Sweetness preferences
        sweet = cust.get("sweetness", "2/5")
        try:
            val = int(str(sweet).split("/")[0])
            if val == 0:
                sweetness_dist["0 (Unsweet)"] += item.quantity
            elif val == 1:
                sweetness_dist["1 (Subtle)"] += item.quantity
            elif val == 2:
                sweetness_dist["2 (Balanced)"] += item.quantity
            else:
                sweetness_dist["3+ (Sweet)"] += item.quantity
        except Exception:
            sweetness_dist["2 (Balanced)"] += item.quantity

    # Top drinks sorted
    top_drinks = sorted(
        [{"name": k, "sold": v} for k, v in drink_sales.items()],
        key=lambda x: x["sold"],
        reverse=True
    )[:5]

    # Category Breakdown via Menu Items
    menu_catalog = {m.name: m.category for m in db.query(MenuItem).all()}
    category_counts = {}
    for item in order_items:
        cat = menu_catalog.get(item.item_name, "Specialty")
        category_counts[cat] = category_counts.get(cat, 0) + item.quantity

    # Simulated Peak Hours Trend (based on real created_at hours or defaults)
    hourly_trend = {
        "08:00": 0, "09:00": 0, "10:00": 0, "11:00": 0, 
        "12:00": 0, "13:00": 0, "14:00": 0, "15:00": 0
    }
    for o in orders:
        if o.created_at:
            h_str = f"{o.created_at.strftime('%H')}:00"
            if h_str in hourly_trend:
                hourly_trend[h_str] += 1
            else:
                hourly_trend["09:00"] += 1

    return {
        "kpis": {
            "total_orders": total_orders,
            "active_orders": active_orders,
            "completed_orders": completed_orders,
            "total_revenue": round(total_revenue, 2),
            "avg_order_value": round(avg_order_value, 2),
            "today_orders": today_orders_count,
            "today_revenue": round(today_revenue, 2),
            "average_rating": round(float(avg_rating), 1),
            "total_reviews": feedback_count,
            "positive_sentiment_pct": round(positive_sentiment_pct, 1),
            "completion_rate_pct": round((completed_orders / total_orders * 100) if total_orders > 0 else 100.0, 1)
        },
        "top_drinks": top_drinks,
        "category_distribution": category_counts,
        "milk_distribution": milk_dist,
        "temperature_distribution": temp_dist,
        "sweetness_distribution": sweetness_dist,
        "rating_histogram": rating_histogram,
        "hourly_trend": hourly_trend,
        "recent_feedbacks": [f.to_dict() for f in recent_feedbacks]
    }
