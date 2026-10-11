from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.db.models import MenuItem

router = APIRouter(prefix="/api/menu", tags=["Menu"])

@router.get("")
def list_menu_items(
    category: Optional[str] = Query(None, description="Filter by category"),
    roast: Optional[str] = Query(None, description="Filter by roast level"),
    temperature: Optional[str] = Query(None, description="Filter by Hot/Iced"),
    search: Optional[str] = Query(None, description="Search name or flavor notes"),
    db: Session = Depends(get_db)
):
    query = db.query(MenuItem).filter(MenuItem.is_available == True)

    if category and category != "All":
        query = query.filter(MenuItem.category == category)
    if roast and roast != "All":
        query = query.filter(MenuItem.roast_level == roast)
    if temperature and temperature != "All":
        query = query.filter(MenuItem.temperature_default == temperature)
    if search:
        search_filter = f"%{search.lower()}%"
        query = query.filter(
            (MenuItem.name.ilike(search_filter)) |
            (MenuItem.description.ilike(search_filter))
        )

    items = query.order_by(MenuItem.is_featured.desc(), MenuItem.id.asc()).all()
    return [item.to_dict() for item in items]

@router.get("/{item_id}")
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item.to_dict()
