import os
import json
import logging
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self._client = None
        self.model_name = settings.GEMINI_MODEL
        self.project_id = settings.PROJECT_ID
        self.location = settings.VERTEX_LOCATION

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location
            )
        return self._client

    def get_recommendations(
        self,
        preferences: Dict[str, Any],
        menu_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Uses Gemini to recommend top 3 coffee drinks from the menu based on customer taste profile or craving.
        """
        craving_prompt = preferences.get("craving_prompt", "")
        preferred_roast = preferences.get("preferred_roast", "Any")
        sweetness_pref = preferences.get("sweetness_pref", 2)
        milk_pref = preferences.get("milk_pref", "Any")
        temperature_pref = preferences.get("temperature_pref", "Any")
        caffeine_pref = preferences.get("caffeine_pref", "Any")
        dietary_notes = preferences.get("dietary_notes", "")

        # Prepare compact menu context
        menu_context = []
        for item in menu_items:
            menu_context.append({
                "id": item["id"],
                "name": item["name"],
                "category": item["category"],
                "roast_level": item["roast_level"],
                "sweetness_level": item["sweetness_level"],
                "caffeine_level": item["caffeine_level"],
                "flavor_notes": item["flavor_notes"],
                "milk_options": item["milk_options"],
                "temperature_default": item["temperature_default"],
                "description": item["description"],
                "price": item["price"]
            })

        system_instruction = (
            "You are SipSense's Master Coffee Sommelier and Barista AI. "
            "Analyze the customer's sensory preferences and recommend the top 2-3 drinks from the provided menu. "
            "Return strictly valid JSON with no markdown backticks, matching this exact schema:\n"
            "{\n"
            '  "sommelier_note": "A warm, personal 1-2 sentence greeting and flavor summary",\n'
            '  "recommendations": [\n'
            "    {\n"
            '      "item_id": 1,\n'
            '      "match_score": 96,\n'
            '      "headline": "Punchy 3-5 word descriptor",\n'
            '      "why_you_will_love_it": "Sensory breakdown of how roast, notes, and milk match their palate",\n'
            '      "suggested_tweak": "Barista recommendation (e.g. Try with oat milk for velvet mouthfeel)"\n'
            "    }\n"
            "  ]\n"
            "}"
        )

        user_content = f"""
Customer Palate Profile:
- Craving / Freeform Request: {craving_prompt or 'None provided'}
- Preferred Roast: {preferred_roast}
- Sweetness Preference: {sweetness_pref} / 5 (0 = completely unsweetened, 5 = dessert sweet)
- Preferred Milk: {milk_pref}
- Preferred Temperature: {temperature_pref}
- Caffeine Needs: {caffeine_pref}
- Dietary Notes: {dietary_notes or 'None'}

Available Menu Catalog:
{json.dumps(menu_context, indent=2)}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            raw_text = response.text.strip()
            # Clean possible markdown wrap
            if raw_text.startswith("```"):
                lines = raw_text.splitlines()
                raw_text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            data = json.loads(raw_text)
            return data
        except Exception as e:
            logger.error(f"Gemini recommendation failed: {e}")
            # Heuristic fallback if API error
            return self._fallback_recommendation(preferences, menu_items)

    def _fallback_recommendation(self, preferences: Dict[str, Any], menu_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Heuristic recommendation fallback in case of network timeout."""
        temp_pref = preferences.get("temperature_pref", "Any")
        candidates = menu_items
        if temp_pref in ["Hot", "Iced"]:
            candidates = [m for m in menu_items if m["temperature_default"] == temp_pref] or menu_items
        
        top_items = candidates[:3]
        return {
            "sommelier_note": "Curated specially by our barista team to match your preferred sensory notes.",
            "recommendations": [
                {
                    "item_id": item["id"],
                    "match_score": 92 - (idx * 5),
                    "headline": f"Artisanal {item['category']} Selection",
                    "why_you_will_love_it": item["description"],
                    "suggested_tweak": f"Pairs wonderfully with {item['milk_options'][0] if item.get('milk_options') else 'pure black'}"
                }
                for idx, item in enumerate(top_items)
            ]
        }

    def chat_barista(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        menu_items: List[Dict[str, Any]]
    ) -> str:
        """
        Conversational assistant answering coffee queries, menu explanations, and drink pairings.
        """
        menu_summary = ", ".join([f"{item['name']} (${item['price']:.2f}, {item['category']}, {item['roast_level']} roast)" for item in menu_items])

        system_instruction = (
            f"You are 'SipSense Sommelier', an approachable, passionate specialty coffee expert and barista at SipSense AI cafe. "
            f"You love helping guests discover their ideal brew, explaining bean origins, roast chemistry, tasting notes, and food pairings. "
            f"The cafe's current active menu includes: {menu_summary}. "
            f"Keep your answers concise, warm, sensory-rich, and directly reference our menu items when relevant. "
            f"Do not invent drinks not on the menu, but you can suggest customizations (milk types, syrup adjustments, extra shots)."
        )

        contents = []
        for chat in chat_history[-6:]:  # Keep recent context
            contents.append(f"{chat['role'].capitalize()}: {chat['content']}")
        contents.append(f"Customer: {message}")
        prompt_text = "\n".join(contents)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.6,
                    max_output_tokens=300
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini chat failed: {e}")
            return "I'm having a brief connection flutter, but I'd love to suggest our Nitro Cold Brew with Vanilla Sweet Cream or our signature Cardamom Rose Pistachio Latte!"

    def summarize_feedback(self, rating: int, comment: str, item_names: List[str]) -> str:
        """
        Analyzes customer feedback and generates concise barista intelligence.
        """
        if not comment:
            return f"Customer rated {rating}/5 stars."
        
        prompt = (
            f"Summarize this customer feedback in 1 concise sentence highlighting key flavor or service sentiment:\n"
            f"Items ordered: {', '.join(item_names)}\n"
            f"Rating: {rating}/5\n"
            f"Comment: '{comment}'"
        )
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=100)
            )
            return response.text.strip()
        except Exception:
            return f"Rating {rating}/5. Customer feedback recorded."

gemini_service = GeminiService()
