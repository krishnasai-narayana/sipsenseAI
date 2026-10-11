import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Reconfigure stdout for utf-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

LOCAL_BASE = "http://127.0.0.1:8000"
PROD_BASE = "https://sipsense-app-239920603011.asia-south1.run.app"

def run_e2e_suite():
    print("=" * 80)
    print("SipSense AI — Complete End-to-End Application & Cloud Services Test Suite")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    results = []

    def record_test(name, passed, detail=""):
        status = "PASSED [OK]" if passed else "FAILED [X]"
        print(f"  {status:<14} | {name:<45} | {detail}")
        results.append((name, passed, detail))

    # -------------------------------------------------------------
    # 1. DATABASE & HEALTH CHECKS
    # -------------------------------------------------------------
    print("\n[Phase 1] Cloud SQL & FastAPI Health Checks")
    print("-" * 80)

    try:
        r = requests.get(f"{LOCAL_BASE}/health", timeout=5)
        passed = r.status_code == 200 and r.json().get("status") == "healthy"
        record_test("Local FastAPI & DB /health", passed, f"status: {r.status_code}")
    except Exception as e:
        record_test("Local FastAPI & DB /health", False, str(e))

    try:
        r = requests.get(f"{PROD_BASE}/health", timeout=10)
        passed = r.status_code == 200 and r.json().get("status") == "healthy"
        record_test("Cloud Run Production /health", passed, f"status: {r.status_code}")
    except Exception as e:
        record_test("Cloud Run Production /health", False, str(e))

    # -------------------------------------------------------------
    # 2. MENU CATALOG RETRIEVAL
    # -------------------------------------------------------------
    print("\n[Phase 2] Menu Catalog & Cloud SQL Data Integrity")
    print("-" * 80)

    menu_item_id = 1
    try:
        r = requests.get(f"{LOCAL_BASE}/api/menu", timeout=5)
        data = r.json()
        passed = r.status_code == 200 and len(data) >= 10
        if passed and len(data) > 0:
            menu_item_id = data[0]["id"]
        record_test("Menu Catalog (/api/menu)", passed, f"{len(data)} artisanal drinks loaded")
    except Exception as e:
        record_test("Menu Catalog (/api/menu)", False, str(e))

    # -------------------------------------------------------------
    # 3. VERTEX AI / GEMINI 2.5 FLASH SENSORY PIPELINES
    # -------------------------------------------------------------
    print("\n[Phase 3] Vertex AI / Gemini 2.5 Flash Sensory Intelligence")
    print("-" * 80)

    # Craving search
    try:
        payload = {"craving_text": "I want an ultra-smooth oat milk drink with hazelnut and delicate sweetness"}
        r = requests.post(f"{LOCAL_BASE}/api/recommendations/craving", json=payload, timeout=15)
        data = r.json()
        passed = r.status_code == 200 and "recommendations" in data and len(data["recommendations"]) > 0
        detail = f"AI Sommelier returned {len(data.get('recommendations', []))} tasting cards"
        record_test("Gemini Craving Search (/recommendations/craving)", passed, detail)
    except Exception as e:
        record_test("Gemini Craving Search (/recommendations/craving)", False, str(e))

    # Palate Matchmaker
    try:
        payload = {
            "preferred_roast": "Medium",
            "sweetness_pref": 3,
            "milk_pref": "Oat Milk",
            "temperature_pref": "Iced",
            "caffeine_pref": "High",
            "favorite_flavors": ["Brown Sugar", "Cinnamon"],
            "session_id": "e2e_tester_session"
        }
        r = requests.post(f"{LOCAL_BASE}/api/recommendations/matchmaker", json=payload, timeout=15)
        data = r.json()
        passed = r.status_code == 200 and "recommendations" in data
        record_test("Gemini Palate Matchmaker Quiz", passed, f"Matched {len(data.get('recommendations', []))} drinks")
    except Exception as e:
        record_test("Gemini Palate Matchmaker Quiz", False, str(e))

    # Conversational Chatbot
    try:
        payload = {
            "message": "What is the caffeine difference between your nitro cold brew and pour over?",
            "history": []
        }
        r = requests.post(f"{LOCAL_BASE}/api/ai/chat", json=payload, timeout=15)
        data = r.json()
        passed = r.status_code == 200 and len(data.get("reply", "")) > 10
        record_test("Gemini Conversational Sommelier Chat (/api/ai/chat)", passed, f"Reply: {data.get('reply','')[:40]}...")
    except Exception as e:
        record_test("Gemini Conversational Sommelier Chat (/api/ai/chat)", False, str(e))

    # -------------------------------------------------------------
    # 4. FULL ORDER LIFECYCLE, TABLE ROUTING & QUEUE ENGINE
    # -------------------------------------------------------------
    print("\n[Phase 4] End-to-End Order Lifecycle & Real-Time Barista Queue")
    print("-" * 80)

    order_id = None
    try:
        order_payload = {
            "customer_name": "E2E Verification Guest",
            "customer_phone": "+1 (555) 999-8888",
            "session_id": "e2e_guest_session_1",
            "special_instructions": "Table 2 (Sensory Bar) • Extra hot oat milk",
            "items": [
                {
                    "menu_item_id": menu_item_id,
                    "quantity": 1,
                    "customizations": {
                        "milk": "Oat Milk",
                        "sweetness": "2/5",
                        "temperature": "Hot",
                        "extra_shots": 1,
                        "notes": "Table 2 (Sensory Bar)"
                    }
                }
            ]
        }
        r = requests.post(f"{LOCAL_BASE}/api/orders", json=order_payload, timeout=10)
        data = r.json()
        passed = r.status_code == 200 and "id" in data
        if passed:
            order_id = data["id"]
        record_test("Order Creation with Table Routing", passed, f"Order #{order_id} total: ${data.get('total_amount', 0)}")
    except Exception as e:
        record_test("Order Creation with Table Routing", False, str(e))

    # Order tracking
    if order_id:
        try:
            r = requests.get(f"{LOCAL_BASE}/api/orders/{order_id}", timeout=5)
            data = r.json()
            passed = r.status_code == 200 and data.get("status") == "PLACED"
            record_test("Order Tracking & Wait-Time Calculation", passed, f"Status: {data.get('status')}, Wait: {data.get('estimated_wait_minutes')}m")
        except Exception as e:
            record_test("Order Tracking & Wait-Time Calculation", False, str(e))

        # Status advance: PLACED -> BREWING
        try:
            r = requests.post(f"{LOCAL_BASE}/api/orders/{order_id}/status", json={"status": "BREWING"}, timeout=5)
            passed = r.status_code == 200 and r.json().get("status") == "BREWING"
            record_test("Barista Dispatch: Advance to BREWING", passed, f"Status: {r.json().get('status')}")
        except Exception as e:
            record_test("Barista Dispatch: Advance to BREWING", False, str(e))

        # Status advance: BREWING -> READY
        try:
            r = requests.post(f"{LOCAL_BASE}/api/orders/{order_id}/status", json={"status": "READY"}, timeout=5)
            passed = r.status_code == 200 and r.json().get("status") == "READY"
            record_test("Barista Dispatch: Advance to READY", passed, f"Pickup PIN: #{r.json().get('pickup_code')}")
        except Exception as e:
            record_test("Barista Dispatch: Advance to READY", False, str(e))

        # Status advance: READY -> COMPLETED
        try:
            r = requests.post(f"{LOCAL_BASE}/api/orders/{order_id}/status", json={"status": "COMPLETED"}, timeout=5)
            passed = r.status_code == 200 and r.json().get("status") == "COMPLETED"
            record_test("Barista Dispatch: Mark COMPLETED", passed, "Drink handed over to guest")
        except Exception as e:
            record_test("Barista Dispatch: Mark COMPLETED", False, str(e))

        # Customer Feedback & Gemini Sentiment Analysis
        try:
            fb_payload = {
                "rating": 5,
                "taste_score": 5,
                "comment": "Super velvety microfoam and rich single origin profile. Exceptional cup!"
            }
            r = requests.post(f"{LOCAL_BASE}/api/orders/{order_id}/feedback", json=fb_payload, timeout=15)
            data = r.json()
            passed = r.status_code == 200 and "ai_sentiment_summary" in data and len(data["ai_sentiment_summary"]) > 0
            detail = f"Gemini Sentiment: '{data.get('ai_sentiment_summary','')[:45]}...'"
            record_test("Gemini Taste Feedback & Sentiment Analysis", passed, detail)
        except Exception as e:
            record_test("Gemini Taste Feedback & Sentiment Analysis", False, str(e))

    # -------------------------------------------------------------
    # 5. ROASTERY ANALYTICS & INSIGHTS ENGINE
    # -------------------------------------------------------------
    print("\n[Phase 5] Roastery Business Intelligence & Analytics Visualizations")
    print("-" * 80)

    try:
        r = requests.get(f"{LOCAL_BASE}/api/analytics/insights", timeout=5)
        data = r.json()
        kpis = data.get("kpis", {})
        passed = (
            r.status_code == 200 and
            kpis.get("total_orders", 0) > 0 and
            "hourly_trend" in data and
            "milk_distribution" in data and
            "top_drinks" in data
        )
        detail = (
            f"Revenue: ${kpis.get('total_revenue',0)} | "
            f"Orders: {kpis.get('total_orders',0)} | "
            f"Avg Rating: {kpis.get('average_rating')}★ | "
            f"Top Drink: {data.get('top_drinks', [{}])[0].get('name', 'N/A')}"
        )
        record_test("Roastery Analytics Engine (/api/analytics/insights)", passed, detail)
    except Exception as e:
        record_test("Roastery Analytics Engine (/api/analytics/insights)", False, str(e))

    # -------------------------------------------------------------
    # 6. STATIC ASSETS & STANDALONE DEMO
    # -------------------------------------------------------------
    print("\n[Phase 6] Client Web Application & Standalone Demo")
    print("-" * 80)

    try:
        r = requests.get(f"{LOCAL_BASE}/", timeout=5)
        passed = r.status_code == 200 and "SipSense" in r.text
        record_test("Customer Web App (/) HTML", passed, f"Size: {len(r.text)} bytes")
    except Exception as e:
        record_test("Customer Web App (/) HTML", False, str(e))

    try:
        r = requests.get(f"{LOCAL_BASE}/static/demo.html", timeout=5)
        passed = r.status_code == 200 and "Offline Interactive Engine" in r.text
        record_test("Offline/Online Showcase (/static/demo.html)", passed, f"Size: {len(r.text)} bytes")
    except Exception as e:
        record_test("Offline/Online Showcase (/static/demo.html)", False, str(e))

    # Summary
    print("\n" + "=" * 80)
    passed_count = sum(1 for _, p, _ in results if p)
    total_count = len(results)
    print(f"TEST RUN COMPLETED: {passed_count}/{total_count} TESTS PASSED ({(passed_count/total_count)*100:.1f}%)")
    print("=" * 80)

    if passed_count == total_count:
        print("ALL END-TO-END TESTS PASSED! System is completely operational.\n")
        return True
    else:
        print(f"WARNING: {total_count - passed_count} tests failed.\n")
        return False

if __name__ == "__main__":
    success = run_e2e_suite()
    sys.exit(0 if success else 1)
