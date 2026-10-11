from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.db.session import get_db
from app.db.models import MenuItem, CustomerPreference
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/api/ai", tags=["Vertex AI / Gemini"])

class RecommendationRequest(BaseModel):
    session_id: str = Field(..., description="Unique user browser session")
    craving_prompt: Optional[str] = Field(None, description="Freeform craving or description")
    preferred_roast: Optional[str] = "Any"
    sweetness_pref: Optional[int] = 2
    milk_pref: Optional[str] = "Any"
    temperature_pref: Optional[str] = "Any"
    caffeine_pref: Optional[str] = "Any"
    dietary_notes: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

@router.post("/recommend")
def get_recommendations(req: RecommendationRequest, db: Session = Depends(get_db)):
    # Save/record preference
    pref = CustomerPreference(
        session_id=req.session_id,
        preferred_roast=req.preferred_roast,
        sweetness_pref=req.sweetness_pref,
        milk_pref=req.milk_pref,
        temperature_pref=req.temperature_pref,
        caffeine_pref=req.caffeine_pref,
        dietary_notes=req.dietary_notes
    )
    db.add(pref)
    db.commit()

    menu_items = [m.to_dict() for m in db.query(MenuItem).filter(MenuItem.is_available == True).all()]
    if not menu_items:
        raise HTTPException(status_code=400, detail="No menu items available")

    ai_result = gemini_service.get_recommendations(req.model_dump(), menu_items)
    
    # Enrich recommendation response with full item card data
    menu_dict = {m["id"]: m for m in menu_items}
    enriched_recs = []
    for rec in ai_result.get("recommendations", []):
        item_id = rec.get("item_id")
        if item_id in menu_dict:
            item_data = dict(menu_dict[item_id])
            item_data["match_score"] = rec.get("match_score", 90)
            item_data["headline"] = rec.get("headline", "Sommelier Match")
            item_data["why_you_will_love_it"] = rec.get("why_you_will_love_it", "")
            item_data["suggested_tweak"] = rec.get("suggested_tweak", "")
            enriched_recs.append(item_data)
        elif menu_items:
            # Fallback to first available if ID mismatched
            fallback_item = dict(menu_items[0])
            fallback_item["match_score"] = 88
            fallback_item["headline"] = rec.get("headline", "Barista Special")
            fallback_item["why_you_will_love_it"] = rec.get("why_you_will_love_it", fallback_item["description"])
            fallback_item["suggested_tweak"] = rec.get("suggested_tweak", "Try iced or hot")
            enriched_recs.append(fallback_item)

    return {
        "sommelier_note": ai_result.get("sommelier_note", "Here are your tailored coffee recommendations."),
        "recommendations": enriched_recs
    }

@router.post("/chat")
def chat_with_barista(req: ChatRequest, db: Session = Depends(get_db)):
    menu_items = [m.to_dict() for m in db.query(MenuItem).filter(MenuItem.is_available == True).all()]
    chat_history = [c.model_dump() for c in req.history]
    reply = gemini_service.chat_barista(req.message, chat_history, menu_items)
    return {"reply": reply}
