# SipSense AI ☕

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Google Cloud Run](https://img.shields.io/badge/Google_Cloud_Run-Deployed-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Cloud SQL PostgreSQL](https://img.shields.io/badge/Cloud_SQL-PostgreSQL_18-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://cloud.google.com/sql)
[![Google Gemini](https://img.shields.io/badge/Vertex_AI-Gemini_2.5_Flash-8E75C4?style=for-the-badge&logo=google&logoColor=white)](https://cloud.google.com/vertex-ai)

> **Next-Generation Artisanal Coffee Discovery, Sensory AI Sommelier, and Real-Time Barista Queue System**

---

## 🌟 Interactive Demos & Live Links

| Platform / View | Link | Description |
| :--- | :--- | :--- |
| 🌐 **Production Cloud Run App** | [https://sipsense-app-239920603011.asia-south1.run.app](https://sipsense-app-239920603011.asia-south1.run.app) | Live customer web app connected to Cloud SQL & Vertex AI Gemini 2.5 |
| 💻 **Interactive Showcase (Online / Offline)** | [https://sipsense-app-239920603011.asia-south1.run.app/static/demo.html](https://sipsense-app-239920603011.asia-south1.run.app/static/demo.html) | Standalone interactive showcase with offline mode & toggle to Cloud Run |
| 📂 **Local Offline Demo File** | [demo.html](demo.html) or [docs/index.html](docs/index.html) | Double-click to open in any browser! Zero install, works 100% offline |
| 📖 **Interactive Swagger / OpenAPI** | [https://sipsense-app-239920603011.asia-south1.run.app/docs](https://sipsense-app-239920603011.asia-south1.run.app/docs) | Live API documentation and interactive test harness |
| 🩺 **System Health Check** | [https://sipsense-app-239920603011.asia-south1.run.app/health](https://sipsense-app-239920603011.asia-south1.run.app/health) | Real-time database & AI service diagnostics |

---

## 📸 Interface Showcase

<div align="center">
  <img src="assets/sipsense_ui_overview.jpg" alt="SipSense AI Overview" width="850px" style="border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);" />
  <p><em>Gemini AI Sommelier Tasting Flight with Craving Search, Sensory Match Percentage, and Roastery Catalog</em></p>
  <br/>
  <img src="assets/sipsense_customizer_ui.jpg" alt="SipSense Drink Customizer & Cart" width="850px" style="border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);" />
  <p><em>Artisanal Drink Customizer (Milk options, sweetness scale, extra shots) & Coffee Cup Checkout Drawer</em></p>
</div>

---

## ⚡ Try the Interactive Demo (Zero Installation Required)

Want to explore the app immediately without configuring Google Cloud credentials or local databases?

1. Clone the repository:
   ```bash
   git clone https://github.com/krishnasai-narayana/sipsenseAI.git
   ```
2. Double-click **[`demo.html`](demo.html)** to open it directly in your browser.
3. **What you can do offline**:
   - **✨ Ask Gemini**: Type any flavor craving (e.g. *"Craving something with oat milk, hazelnut, and low acid"*) and receive curated Tasting Flights with AI match scores.
   - **⚙️ Drink Customizer**: Click **"⚙ Customize & Add"** to change milks, sweetness level (0-5), temperature, and extra espresso shots with dynamic price calculation.
   - **⚡ Quick Add**: Instant 1-click addition directly to your cup.
   - **🛒 Coffee Cup Drawer**: View itemized subtotal, artisanal tax, and tap **"Send to Barista Station 🚀"**.
   - **📍 Order Tracker**: Watch the animated lifecycle stepper simulate preparation states.
   - **📋 Barista Board**: Open the barista production station to advance tickets from *Received* ➜ *Brewing* ➜ *Ready*.
   - **🌐 Online Switch**: Click the engine button in the top banner to switch seamlessly between the **Offline Interactive Engine** and the **Live Cloud Run API**!

---

## 📐 System Architecture

```mermaid
graph TD
    Client["📱 Customer Web App<br/>(Mobile QR Discovery · Customizer · Order Tracker)"] -->|HTTPS REST| CloudRun["⚡ FastAPI on Google Cloud Run<br/>(Order Logic · Wait Time Queue Engine)"]
    
    CloudRun -->|Unix Domain Socket / Cloud SQL Proxy| CloudSQL[("🗄️ Cloud SQL PostgreSQL 18<br/>(Menu · Preferences · Orders · Feedback)")]
    CloudRun -->|google-genai SDK| Gemini["🧠 Vertex AI / Gemini 2.5 Flash<br/>(Palate Chemistry · AI Sommelier · Sentiment)"]
    
    Barista["🧑‍🍳 Barista Live Board"] -->|Status Update| CloudRun
```

### Architectural Highlights
1. **Customer Web App**: Responsive mobile-first interface designed with an artisanal dark espresso aesthetic, smooth glassmorphism, micro-animations, and live queue polling.
2. **FastAPI Engine**: Asynchronous Python backend executing order lifecycle state transitions, subtotal calculation with customizations, and dynamic wait-time estimation based on active tickets.
3. **Vertex AI / Gemini 2.5 Flash**: Multi-dimensional sensory analysis matching customer cravings (roast, sweetness, milk profile, acidity, and caffeine tolerance) to active roastery offerings.
4. **Cloud SQL PostgreSQL**: Managed relational persistence running PostgreSQL 18 with connection pooling, indexes, and automated foreign key cascades.

---

## ✨ Core Features

### 1. "Find My Sip" AI Sommelier Matchmaker
- **Freeform Craving Search**: Customers can type natural language desires (e.g., *"Need high energy, low acid, velvety oat milk with nutty cocoa finish"*).
- **Interactive Palate Questionnaire**: 4-step wizard collecting roast level, sweetness (0–5 scale), milk preference, serving temperature, and dietary needs.
- **Tasting Cards**: Returns exact match score percentage, sensory breakdown of why the customer will love it, and custom barista tweaks.

### 2. Conversational Barista AI (Floating Widget)
- Interactive floating chat bubble available anywhere in the app.
- Powered by `gemini-2.5-flash` with full context of the active roastery menu to discuss bean origins, roast chemistry, and pairings.

### 3. Drink Customizer
- Interactive adjustments for:
  - **Milk Alternatives**: Oat Milk, Almond Milk, Farm Fresh Whole Milk, Organic Pistachio Milk, or None.
  - **Sweetness Scale**: Unsweetened (0%), Light (25%), Regular (50%), Extra Sweet (100%).
  - **Temperature**: Hot (Velvet Microfoam), Iced (Over Clear Cubes), or Extra Iced.
  - **Extra Espresso Boost**: +1 or +2 Ristretto Shots (+$0.75 / shot) with real-time price updates.
  - **Barista Preparation Notes**: Special instructions passed directly to the order ticket.

### 4. Real-Time Order Tracking & Queue Engine
- 3-step live progress stepper: **Placed → Brewing → Ready for Pickup**.
- Live queue position calculation (`#1 in line`, `#2 in line`).
- Estimated wait time countdown dynamically computed from active queue volume.
- Unique pickup ticket representation to present at counter.

### 5. Barista Live Workflow Board
- Operational interface for cafe baristas to advance drink lifecycle states.
- Triggers instant live status synchronization to the customer's tracking view.

### 6. Customer Taste Feedback & Sentiment Intelligence
- Post-pickup rating (1–5 stars) and taste balance evaluation.
- Gemini automatically summarizes customer comments into concise barista intelligence.

---

## 🗄️ Database Schema

The database runs on **Google Cloud SQL PostgreSQL** (`sipsense-pg`) under database `sipsense`:

```mermaid
erDiagram
    MENU_ITEMS ||--o{ ORDER_ITEMS : contains
    ORDERS ||--|{ ORDER_ITEMS : includes
    ORDERS ||--o| CUSTOMER_FEEDBACK : receives
    CUSTOMER_PREFERENCES {
        int id PK
        string session_id
        string preferred_roast
        int sweetness_pref
        string milk_pref
        string temperature_pref
        string caffeine_pref
    }
    MENU_ITEMS {
        int id PK
        string name
        string category
        text description
        numeric price
        string roast_level
        string caffeine_level
        string acidity
        int sweetness_level
        string temperature_default
        json milk_options
        json flavor_notes
        boolean is_featured
    }
    ORDERS {
        int id PK
        string order_number
        string customer_name
        string status
        numeric subtotal
        numeric tax
        numeric total_price
        int estimated_wait_minutes
    }
    ORDER_ITEMS {
        int id PK
        int order_id FK
        int menu_item_id FK
        int quantity
        numeric unit_price
        json customizations
    }
    CUSTOMER_FEEDBACK {
        int id PK
        int order_id FK
        int rating
        string comment
        json ai_sentiment_analysis
    }
```

---

## 🛠️ Local Development & Setup

### Prerequisites
- Python 3.11+
- Google Cloud SDK (`gcloud`)
- [Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/connect-auth-proxy) (downloaded as `cloud-sql-proxy.exe`)
- Active GCP Project with Vertex AI and Cloud SQL APIs enabled

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/krishnasai-narayana/sipsenseAI.git
cd sipsenseAI
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```env
PROJECT_ID=sipsense-ai-demo
REGION=asia-south1
VERTEX_LOCATION=us-central1
INSTANCE_CONNECTION_NAME=sipsense-ai-demo:asia-south1:sipsense-pg
DB_NAME=sipsense
DB_USER=sipsense_app
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=5432
GOOGLE_APPLICATION_CREDENTIALS=sa-key.json
GEMINI_MODEL=gemini-2.5-flash
```

### 4. Running the Development Stack
```powershell
# One-click runner starts proxy and uvicorn:
.\run_local.ps1
```
Or start manually:
```powershell
# 1. Start Cloud SQL Auth Proxy:
.\cloud-sql-proxy.exe --credentials-file sa-key.json sipsense-ai-demo:asia-south1:sipsense-pg --port 5432

# 2. Run FastAPI:
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🚀 Cloud Run Deployment

Deploy the containerized application to Google Cloud Run in a single command:

```powershell
.\deploy_cloud_run.ps1
```

Or via `gcloud` CLI:
```powershell
gcloud run deploy sipsense-app `
  --source . `
  --project sipsense-ai-demo `
  --region asia-south1 `
  --platform managed `
  --allow-unauthenticated `
  --service-account=sipsense-app-sa@sipsense-ai-demo.iam.gserviceaccount.com `
  --add-cloudsql-instances=sipsense-ai-demo:asia-south1:sipsense-pg `
  --set-env-vars="PROJECT_ID=sipsense-ai-demo,REGION=asia-south1,VERTEX_LOCATION=us-central1,INSTANCE_CONNECTION_NAME=sipsense-ai-demo:asia-south1:sipsense-pg,DB_NAME=sipsense,DB_USER=sipsense_app,DB_PASSWORD=your_db_password,GEMINI_MODEL=gemini-2.5-flash"
```

---

## 🔒 Security Best Practices

- **Zero Hardcoded Secrets**: Secrets and credentials (`.env`, `sa-key.json`) are excluded in `.gitignore` and `.dockerignore`.
- **Identity-Aware IAM**: Cloud Run utilizes a dedicated least-privilege service account (`sipsense-app-sa`) granted strictly `roles/cloudsql.client` and `roles/aiplatform.user`.
- **Mutual TLS**: Database connections are encrypted end-to-end via Cloud SQL Auth Proxy locally and Unix Domain Sockets on Cloud Run.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Krishna Sai Narayana.
