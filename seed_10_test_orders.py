import sys
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Reconfigure utf-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.db.session import SessionLocal
from app.db.models import MenuItem, Order, OrderItem, CustomerFeedback

def seed_10_orders():
    print("=" * 70)
    print("SipSense AI — Generating 10 Comprehensive Test Orders for End-to-End Testing")
    print("=" * 70)

    db = SessionLocal()
    try:
        menu_items = db.query(MenuItem).all()
        if not menu_items:
            print("[ERROR] No menu items found in database. Seed menu first.")
            return

        menu_dict = {item.name: item for item in menu_items}

        test_customers = [
            {"name": "Sophia Laurent", "phone": "+1 (555) 234-5678", "table": "Table 1 (Window View)"},
            {"name": "David Chen", "phone": "+1 (555) 345-6789", "table": "Table 2 (Sensory Bar)"},
            {"name": "Amina Khalil", "phone": "+1 (555) 456-7890", "table": "Takeaway Counter"},
            {"name": "Lucas Miller", "phone": "+1 (555) 567-8901", "table": "Table 3 (Roastery Floor)"},
            {"name": "Zoe Patel", "phone": "+1 (555) 678-9012", "table": "Table 4 (Outdoor Patio)"},
            {"name": "Liam Nelson", "phone": "+1 (555) 789-0123", "table": "Table 2 (Sensory Bar)"},
            {"name": "Rachel Green", "phone": "+1 (555) 890-1234", "table": "Takeaway Counter"},
            {"name": "James O'Connor", "phone": "+1 (555) 901-2345", "table": "Table 1 (Window View)"},
            {"name": "Chloe Zhao", "phone": "+1 (555) 012-3456", "table": "Table 4 (Outdoor Patio)"},
            {"name": "Mateo Rossi", "phone": "+1 (555) 123-4567", "table": "Table 3 (Roastery Floor)"}
        ]

        sample_scenarios = [
            # 1
            {
                "status": "COMPLETED",
                "drink": "Brown Sugar Shaken Espresso",
                "milk": "Oat Milk",
                "sweet": "3/5",
                "temp": "Iced",
                "shots": 1,
                "notes": "Extra shaken, light ice",
                "rating": 5,
                "taste": 5,
                "comment": "Outstanding blonde roast clarity with silky demerara finish. Best shaken espresso in town!",
                "ai_summary": "Customer expressed exceptional delight regarding blonde espresso extraction and demerara sweetness balance."
            },
            # 2
            {
                "status": "COMPLETED",
                "drink": "Velvet Flat White",
                "milk": "Whole Milk",
                "sweet": "1/5",
                "temp": "Hot",
                "shots": 0,
                "notes": "Micro-foam extra glossy",
                "rating": 5,
                "taste": 5,
                "comment": "Texture was pure liquid velvet. The caramelized malt notes really shine through.",
                "ai_summary": "Positive feedback on milk steaming technique and medium roast flavor profile integration."
            },
            # 3
            {
                "status": "COMPLETED",
                "drink": "Nitro Cold Brew with Vanilla Sweet Cream",
                "milk": "Oat Milk Foam",
                "sweet": "2/5",
                "temp": "Iced",
                "shots": 0,
                "notes": "Cascade was mesmerizing",
                "rating": 4,
                "taste": 4,
                "comment": "Silky mouthfeel and intense dark cocoa. Sweet cream was balanced without overpowering the cold brew.",
                "ai_summary": "Favorable response to nitrogen infusion cascade and plant-based sweet cream mouthfeel."
            },
            # 4
            {
                "status": "COMPLETED",
                "drink": "Yirgacheffe Citrus Pour Over",
                "milk": "None",
                "sweet": "0/5",
                "temp": "Hot",
                "shots": 0,
                "notes": "Poured at 92C",
                "rating": 5,
                "taste": 5,
                "comment": "Jasmine fragrance was enchanting. Clean Meyer lemon finish with zero astringency.",
                "ai_summary": "High appreciation for single-origin Ethiopian washed clarity and floral cup score."
            },
            # 5
            {
                "status": "COMPLETED",
                "drink": "Cardamom & Rose Botanical Latte",
                "milk": "Oat Milk",
                "sweet": "3/5",
                "temp": "Hot",
                "shots": 1,
                "notes": "Pistachio dust garnish",
                "rating": 5,
                "taste": 5,
                "comment": "Cardamom and Damascus rose combination was exotic and soothing. A sensory masterpiece.",
                "ai_summary": "Customer enthusiastically commended botanical spice synergy and steamed oat milk harmony."
            },
            # 6
            {
                "status": "READY",
                "drink": "Kyoto Style Slow-Drip Cold Brew",
                "milk": "None",
                "sweet": "1/5",
                "temp": "Iced",
                "shots": 0,
                "notes": "Over large crystal cube",
                "rating": None
            },
            # 7
            {
                "status": "READY",
                "drink": "Panama Geisha Natural Reserve",
                "milk": "None",
                "sweet": "2/5",
                "temp": "Hot",
                "shots": 0,
                "notes": "Boquete harvest",
                "rating": None
            },
            # 8
            {
                "status": "BREWING",
                "drink": "Brown Sugar Shaken Espresso",
                "milk": "Almond Milk",
                "sweet": "2/5",
                "temp": "Iced",
                "shots": 2,
                "notes": "Double caffeine boost",
                "rating": None
            },
            # 9
            {
                "status": "BREWING",
                "drink": "Spanish Smoked Honey Cortado",
                "milk": "Whole Milk",
                "sweet": "2/5",
                "temp": "Hot",
                "shots": 0,
                "notes": "Smoked paprika dusting",
                "rating": None
            },
            # 10
            {
                "status": "PLACED",
                "drink": "Sea Salt Caramel Macchiato",
                "milk": "Oat Milk",
                "sweet": "4/5",
                "temp": "Hot",
                "shots": 1,
                "notes": "Extra fleur de sel caramel drizzle",
                "rating": None
            }
        ]

        created_orders = []

        for i, (cust, scn) in enumerate(zip(test_customers, sample_scenarios)):
            order_num = f"SIP-{random.randint(1000, 9999)}"
            pickup_code = str(random.randint(100, 999))
            
            # Find menu item
            drink_item = menu_dict.get(scn["drink"], menu_items[0])
            unit_price = float(drink_item.price) + (scn["shots"] * 0.75)
            quantity = 1
            subtotal = unit_price * quantity
            tax = round(subtotal * 0.08, 2)
            total_price = subtotal + tax

            # Stagger timestamps across the morning (e.g. 8:15 AM to 11:45 AM)
            minutes_ago = (10 - i) * 20
            created_time = datetime.utcnow() - timedelta(minutes=minutes_ago)

            customizations = {
                "milk": scn["milk"],
                "sweetness": scn["sweet"],
                "temperature": scn["temp"],
                "extra_shots": scn["shots"],
                "notes": scn["notes"]
            }

            order = Order(
                id=order_num,
                session_id=f"test_sess_{i+1}",
                customer_name=cust["name"],
                customer_phone=cust["phone"],
                status=scn["status"],
                total_amount=total_price,
                estimated_wait_minutes=random.choice([3, 5, 7]) if scn["status"] in ["PLACED", "BREWING"] else 0,
                pickup_code=pickup_code,
                special_instructions=f"{cust['table']} • {scn['notes']}",
                created_at=created_time,
                updated_at=created_time + timedelta(minutes=random.randint(2, 6))
            )
            db.add(order)
            db.flush()

            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=drink_item.id,
                item_name=drink_item.name,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal,
                customizations=customizations
            )
            db.add(order_item)
            db.flush()

            # If completed, add customer feedback
            if scn["rating"] is not None:
                feedback = CustomerFeedback(
                    order_id=order.id,
                    rating=scn["rating"],
                    taste_score=scn["taste"],
                    comment=scn["comment"],
                    ai_sentiment_summary=scn["ai_summary"],
                    created_at=created_time + timedelta(minutes=8)
                )
                db.add(feedback)

            created_orders.append((order, drink_item, scn))

        db.commit()

        print(f"Successfully generated {len(created_orders)} comprehensive test orders:\n")
        print(f"{'Order ID':<10} | {'Customer':<17} | {'Status':<10} | {'Drink':<35} | {'Total':<7} | {'Pickup'}")
        print("-" * 95)
        for ord_obj, drink, scn in created_orders:
            print(f"{ord_obj.id:<10} | {ord_obj.customer_name:<17} | {ord_obj.status:<10} | {drink.name:<35} | ${ord_obj.total_amount:<6.2f} | #{ord_obj.pickup_code}")
        print("=" * 70)
        print("End-to-end test records committed to Cloud SQL successfully!")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seeding failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_10_orders()
