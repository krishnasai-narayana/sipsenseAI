import sys
import requests
import json

BASE_URL = "https://sipsense-app-239920603011.asia-south1.run.app"

print("=" * 65)
print(f"SipSense AI - Cloud Run End-to-End Verification")
print(f"Target: {BASE_URL}")
print("=" * 65)

# 1. Health
print("\n[1/5] Checking Cloud Run Service Health...")
r = requests.get(f"{BASE_URL}/health", timeout=10)
r.raise_for_status()
print(f"      [OK] Response: {r.json()}")

# 2. Menu Catalog from Cloud SQL
print("\n[2/5] Fetching Menu from Cloud SQL PostgreSQL via Cloud Run...")
r = requests.get(f"{BASE_URL}/api/menu", timeout=10)
r.raise_for_status()
items = r.json()
print(f"      [OK] Retrieved {len(items)} drinks from Cloud SQL.")
print(f"      Sample: {items[0]['name']} (${items[0]['price']:.2f})")

# 3. Vertex AI Gemini Recommendation
print("\n[3/5] Requesting Taste Recommendation from Vertex AI...")
rec_payload = {
    "session_id": "test_suite_run",
    "craving_prompt": "Cold brew with dark cocoa and velvety cream"
}
r = requests.post(f"{BASE_URL}/api/ai/recommend", json=rec_payload, timeout=45)
r.raise_for_status()
rec_data = r.json()
top_pick = rec_data["recommendations"][0]
print(f"      [OK] Gemini Sommelier Note: {rec_data['sommelier_note'][:60]}...")
print(f"      [OK] Top Pick: {top_pick['name']} (Match: {top_pick['match_score']}%)")

# 4. Order Creation to Cloud SQL
print("\n[4/5] Placing Order to Cloud SQL via Cloud Run...")
order_payload = {
    "customer_name": "Antigravity CloudRun Test",
    "session_id": "test_suite_run",
    "items": [{
        "menu_item_id": top_pick["id"],
        "quantity": 1,
        "customizations": {"milk": "Oat Milk Foam", "sweetness": "2/5"}
    }]
}
r = requests.post(f"{BASE_URL}/api/orders", json=order_payload, timeout=10)
r.raise_for_status()
order = r.json()
print(f"      [OK] Order Created: {order['id']}")
print(f"      [OK] Status: {order['status']} | Queue Position: #{order['queue_position']} | PIN: {order['pickup_code']}")

# 5. Order Status Lifecycle Transition
print("\n[5/5] Testing Barista State Machine (PLACED -> BREWING)...")
r = requests.post(f"{BASE_URL}/api/orders/{order['id']}/status", json={"status": "BREWING"}, timeout=10)
r.raise_for_status()
updated = r.json()
print(f"      [OK] Order {order['id']} status advanced to: {updated['status']}")

print("\n" + "=" * 65)
print("SUCCESS: 100% of Cloud Run integrations are connected and healthy!")
print("=" * 65)
