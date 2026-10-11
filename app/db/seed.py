import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure python path includes project root
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
load_dotenv(project_root / ".env")

from app.db.session import engine, SessionLocal, Base
from app.db.models import MenuItem, Order, OrderItem, CustomerFeedback

INITIAL_MENU = [
    {
        "name": "Nitro Cold Brew with Vanilla Sweet Cream",
        "category": "Cold Brew",
        "description": "Slow-steeped for 20 hours, nitrogen-infused for a silky cascade, finished with house-whipped Madagascar vanilla sweet cream.",
        "price": 5.95,
        "roast_level": "Dark",
        "sweetness_level": 2,
        "intensity": 4,
        "caffeine_level": "High",
        "flavor_notes": ["Bourbon Vanilla", "Dark Cocoa", "Velvety Cream"],
        "milk_options": ["Vanilla Sweet Cream", "Oat Milk Foam", "Almond Milk", "None"],
        "temperature_default": "Iced",
        "image_url": "https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&w=800&q=80",
        "is_available": True,
        "is_featured": True,
        "calories": 140
    },
    {
        "name": "Brown Sugar Shaken Espresso",
        "category": "Espresso",
        "description": "Blonde espresso vigorously shaken with caramelized demerara brown sugar, Saigon cinnamon, topped with cold oat milk.",
        "price": 5.75,
        "roast_level": "Light",
        "sweetness_level": 3,
        "intensity": 4,
        "caffeine_level": "High",
        "flavor_notes": ["Demerara Sugar", "Cinnamon", "Oat Mellow"],
        "milk_options": ["Oat Milk", "Almond Milk", "Whole Milk", "Soy Milk"],
        "temperature_default": "Iced",
        "image_url": "https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&w=800&q=80",
        "is_available": True,
        "is_featured": True,
        "calories": 110
    },
    {
        "name": "Cardamom Rose Pistachio Latte",
        "category": "Specialty",
        "description": "Our house signature: double ristretto infused with freshly crushed green cardamom, Damascus rose water, and organic pistachio cream milk.",
        "price": 6.50,
        "roast_level": "Medium",
        "sweetness_level": 2,
        "intensity": 3,
        "caffeine_level": "Medium",
        "flavor_notes": ["Green Cardamom", "Floral Rose", "Toasted Pistachio"],
        "milk_options": ["Pistachio Milk", "Oat Milk", "Whole Milk"],
        "temperature_default": "Hot",
        "image_url": "https://images.unsplash.com/photo-1572442388796-11668a67e53d?auto=format&fit=crop&w=800&q=80",
        "is_available": True,
        "is_featured": True,
        "calories": 190
    },
    {
        "name": "Ethiopian Yirgacheffe Pour Over",
        "category": "Pour Over",
        "description": "Artisanal hand pour over of high-altitude Ethiopian heirloom beans. Exquisite floral clarity with delicate bergamot and jasmine aromatics.",
        "price": 6.25,
        "roast_level": "Light",
        "sweetness_level": 0,
        "intensity": 2,
        "caffeine_level": "Medium",
        "flavor_notes": ["Jasmine Blossom", "Bergamot", "Meyer Lemon", "Peach"],
        "milk_options": ["None (Recommended)", "Side of Oat Milk"],
        "temperature_default": "Hot",
        "image_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=800&q=80",
        "is_available": True,
        "is_featured": False,
        "calories": 5
    },
    {
        "name": "Velvet Flat White",
        "category": "Espresso",
        "description": "Expertly extracted double ristretto layered beneath micro-foamed whole milk creating a dense, glossy sweetness with rich hazelnut depth.",
        "price": 4.95,
        "roast_level": "Medium",
        "sweetness_level": 1,
        "intensity": 3,
        "caffeine_level": "Medium",
        "flavor_notes": ["Roasted Hazelnut", "Caramelized Malt", "Creamy Silk"],
        "milk_options": ["Whole Milk", "Oat Milk", "Almond Milk", "Skim Milk"],
        "temperature_default": "Hot",
        "image_url": "https://images.unsplash.com/photo-1577968897966-3d4325b36b61?auto=format&fit=crop&w=800&q=80",
        "is_available": True,
        "is_featured": False,
        "calories": 130
    },
    {
        "name": "Smoked Sea Salt Caramel Macchiato",
        "category": "Latte & Macchiato",
        "description": "Steamed milk stained with bold double espresso shots, kissed with flaky Brittany smoked sea salt and slow-simmered artisanal caramel.",
        "price": 5.85,
        "roast_level": "Dark",
        "sweetness_level": 4,
        "intensity": 3,
        "caffeine_level": "Medium",
        "flavor_notes": ["Smoked Caramel", "Sea Salt Crunch", "Dark Toffee"],
        "milk_options": ["Whole Milk", "Oat Milk", "Almond Milk"],
        "temperature_default": "Hot",
        "image_url": "https://images.unsplash.com/photo-1485808191679-5f86510681a2?auto=format&fit=crop&w=800&q=80",
        "is_available": True,
        "is_featured": True,
        "calories": 220
    },
    {
        "name": "Ceremonial Uji Matcha Cloud",
        "category": "Specialty",
        "description": "First-harvest ceremonial grade Japanese matcha from Uji, Kyoto, hand-whisked and layered over iced vanilla oat milk with a cold foam cap.",
        "price": 6.75,
        "roast_level": "N/A",
        "sweetness_level": 2,
        "intensity": 3,
        "caffeine_level": "Medium",
        "flavor_notes": ["Umami", "Sweet Grass", "Madagascar Vanilla"],
        "milk_options": ["Oat Milk", "Almond Milk", "Whole Milk"],
        "temperature_default": "Iced",
        "image_url": "https://images.unsplash.com/photo-1536256263959-770b48d82b0a?auto=format&fit=crop&w=800&q=80",
        "is_available": True,
        "is_featured": True,
        "calories": 125
    },
    {
        "name": "Dark Chocolate Seville Orange Mocha",
        "category": "Latte & Macchiato",
        "description": "72% single-origin Belgian dark chocolate ganache, infused with cold-pressed Seville orange zest oil, combined with rich espresso and milk.",
        "price": 6.15,
        "roast_level": "Medium",
        "sweetness_level": 3,
        "intensity": 4,
        "caffeine_level": "Medium",
        "flavor_notes": ["Candied Orange", "72% Dark Chocolate", "Roasted Almond"],
        "milk_options": ["Whole Milk", "Oat Milk", "Almond Milk"],
        "temperature_default": "Hot",
        "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80",
        "is_available": True,
        "is_featured": False,
        "calories": 240
    },
    {
        "name": "Cascara Hibiscus Cold Brew Spritz",
        "category": "Cold Brew",
        "description": "Coffee cherry cascara tea blended with wild organic hibiscus, botanical tonic water, fresh mint, and sparkling effervescence.",
        "price": 5.50,
        "roast_level": "Light",
        "sweetness_level": 2,
        "intensity": 1,
        "caffeine_level": "Low",
        "flavor_notes": ["Tart Cherry", "Cranberry", "Wild Hibiscus", "Tonic Sparkle"],
        "milk_options": ["None"],
        "temperature_default": "Iced",
        "image_url": "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?auto=format&fit=crop&w=800&q=80",
        "is_available": True,
        "is_featured": False,
        "calories": 45
    },
    {
        "name": "Decaf Sugarcane Colombian Cortado",
        "category": "Espresso",
        "description": "Naturally decaffeinated via ethyl acetate sugarcane process preserving all natural fruit esters, cut 1:1 with warm textured whole milk.",
        "price": 4.50,
        "roast_level": "Medium",
        "sweetness_level": 1,
        "intensity": 2,
        "caffeine_level": "Decaf",
        "flavor_notes": ["Panela Cane Sugar", "Red Apple", "Milk Chocolate"],
        "milk_options": ["Whole Milk", "Oat Milk", "Almond Milk"],
        "temperature_default": "Hot",
        "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80",
        "is_available": True,
        "is_featured": False,
        "calories": 60
    }
]

def seed_database():
    print("Creating tables in Cloud SQL PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    db = SessionLocal()
    try:
        # Check existing items
        count = db.query(MenuItem).count()
        if count == 0:
            print(f"Seeding {len(INITIAL_MENU)} initial artisanal menu items...")
            for item_data in INITIAL_MENU:
                item = MenuItem(**item_data)
                db.add(item)
            db.commit()
            print("Menu seeded successfully!")
        else:
            print(f"Database already contains {count} menu items.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
