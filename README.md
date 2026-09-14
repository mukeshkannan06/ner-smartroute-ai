# NER SmartRoute AI — Resilient Route Optimization & Digital Mobility Twin

A production-grade implementation of the architecture: **GIS Network Graph → ML Risk/ETA Models → Multi-Factor Route Optimizer → Digital Mobility Twin → Multi-Lingual AI Assistant → Modern React/Vite Dashboard.**

Every number in this system is computed from a real network graph, trained machine learning models, and accessibility formulas.

---

## 🌟 Key Capabilities

| Component | Status | Implementation Details |
|---|---|---|
| **Road Network GIS Graph** | ✅ Production Ready | 11 arterial cities (Guwahati, Shillong, Silchar, Dimapur, Kohima, Imphal, Jorhat, Aizawl, Tezpur, Nagaon, Agartala) with 17 highway corridors (`networkx`). |
| **Multi-Factor Route Optimizer** | ✅ Production Ready | $k$-shortest paths ranked across distance, duration, road surface, weather hazard, ML risk, and logistics cost. |
| **ML Risk Prediction** | ✅ Production Ready | Real trained `RandomForestClassifier` (scikit-learn) with 88.5% test accuracy evaluating terrain, precipitation, and road quality. |
| **ML ETA Prediction** | ✅ Production Ready | Real trained `GradientBoostingRegressor` (scikit-learn) with ~1 hr MAE on complex mountainous terrains. |
| **Digital Mobility Twin** | ✅ Production Ready | Live disruption simulation (landslides, flash floods, closures), active shipment detection, and automated alternate corridor rerouting. |
| **Unified Routing & OSRM** | ✅ Production Ready | Real OpenStreetMap road geometry routing with graceful offline graph fallback (`backend/services/routing.py`). |
| **Multi-Lingual AI Assistant** | ✅ Production Ready | Conversational assistant supporting 8 languages (English, Tamil, Hindi, Assamese, Manipuri, Bodo, Khasi, Mizo) with tool-calling and UI map sync. |
| **Voice & Speech Synthesis** | ✅ Production Ready | Web Speech API integration for speech recognition and multilingual voice feedback. |
| **Modern React/Vite Frontend** | ✅ Production Ready | High-aesthetic UI with interactive Leaflet GIS map, hazard pulse markers, route comparison cards, simulation panels, and government analytics. |
| **REST API & Swagger Docs** | ✅ Production Ready | FastAPI backend with endpoints for routing, AI chat, digital twin, and government dashboards. |

---

## 🚀 Quick Start Guide

### 1. Backend Setup

```bash
# Optional: Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # On Windows PowerShell

# Install Python dependencies
pip install -r requirements.txt

# Run the test suite (28 tests across routing, AI, services, endpoints)
pytest tests/ -v

# Start the FastAPI Backend Server (Port 8000)
uvicorn backend.main:app --reload --port 8000
```
- **API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Docs (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 2. Frontend Setup (React + Vite)

In a new terminal window:

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite Development Server (Port 3000)
npm run dev
```
- **Live Frontend App**: [http://localhost:3000](http://localhost:3000)

---

### 3. Alternative: Standalone HTML Dashboard

To launch the self-contained single-page dashboard:
```bash
start frontend\ner-smartroute-dashboard.html
```

---

## 🔄 The End-to-End Demonstration Flow

1. **Plan a Route**: Select **Guwahati $\rightarrow$ Imphal** carrying *2 tonnes of Vegetables*. The optimizer ranks 4 alternate highway paths and highlights the recommended corridor on the Leaflet map with ETA, risk probability, and logistics cost.
2. **Simulate a Disruption**: Open the **Digital Twin** tab and trigger a *Landslide* on **NH-001 (Guwahati–Silchar)**.
3. **Inspect Real-time Rerouting**: The system calculates the network impact, detects in-transit shipments, and automatically generates an alternate route via **Dimapur $\rightarrow$ Kohima $\rightarrow$ Imphal**.
4. **Ask the AI Assistant**: Click the floating **AI Assistant** or use the **Microphone** to say *"Find the safest route from Dimapur to Kohima"* or switch language to **हिन्दी**, **தமிழ்**, or **অসমীয়া**.
5. **Government Policy Dashboard**: View the aggregate network accessibility index, critical lifeline corridors, and active hazard warnings.

---

## 📁 Project Architecture

```
ner-smartroute-ai/
├── backend/
│   ├── ai/                     # Chatbot, multilingual templates, intent matching, tools
│   │   ├── chatbot.py          # Conversational execution engine & UI action dispatcher
│   │   ├── intent.py           # Regex & NLP pattern intent classifier
│   │   ├── language.py         # Multi-language translation templates (8 languages)
│   │   ├── prompts.py          # System prompts & guidelines
│   │   └── tools.py            # Tool calling wrappers (route, weather, incidents, twin)
│   ├── services/               # External & Unified Services
│   │   ├── geocoding.py        # Nominatim geocoding with NER coordinate cache
│   │   ├── osrm.py             # OpenStreetMap OSRM road geometry router
│   │   ├── routing.py          # Unified SmartRoute routing engine
│   │   └── weather_service.py  # Weather feed & hazard rating
│   ├── schemas/                # Pydantic request/response schemas
│   ├── models/                 # Database entity & domain models
│   ├── graph_data.py           # 11-city GIS node coordinates & 17 road segments
│   ├── optimizer.py            # NetworkX k-shortest-paths & multi-factor scoring
│   ├── risk_model.py           # RandomForest ML risk predictor
│   ├── eta_model.py            # GradientBoosting ML ETA predictor
│   ├── accessibility.py        # Weighted accessibility index formula
│   ├── digital_twin.py         # Disruption simulation & impact report generator
│   └── main.py                 # FastAPI application wiring REST endpoints
├── frontend/                   # Modern React + Vite Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/         # Sidebar, Header, DataModeBanner
│   │   │   ├── map/            # SmartRouteMap (Leaflet), MapLegend, RouteLayer
│   │   │   ├── routing/        # RoutePlanner, RouteResults, RouteCard, LocationSearch
│   │   │   ├── dashboard/      # GovernmentDashboard, StatCard, CorridorHealthTable
│   │   │   ├── digital_twin/   # DigitalTwin, ImpactReport
│   │   │   └── chat/           # Chatbot, ChatMessage, VoiceButton, LanguageSelector
│   │   ├── context/            # LanguageContext, RouteContext
│   │   ├── hooks/              # useVoice (Web Speech API), useDebounce
│   │   ├── i18n/               # 8 translation files (en, hi, ta, as, mni, brx, kha, lus)
│   │   ├── services/           # api.js, routingService.js, chatService.js
│   │   ├── pages/              # DashboardPage, SmartRoutesPage, DigitalTwinPage, etc.
│   │   ├── App.jsx             # Main application layout
│   │   └── main.jsx            # Entry point
│   ├── package.json
│   └── vite.config.js
├── ml_models/                  # Serialized .pkl machine learning models
├── scripts/
│   └── demo_scenario.py        # Terminal CLI end-to-end demo
└── tests/                      # Automated Pytest suite (28 passing tests)
    ├── test_accessibility.py
    ├── test_ai_chatbot.py
    ├── test_api_endpoints.py
    ├── test_backend_services.py
    ├── test_digital_twin.py
    ├── test_optimizer.py
    └── test_risk.py
```

---

## 🧪 Automated Testing

To run all automated unit and integration tests:

```bash
pytest tests/ -v
```
All 28 tests validate:
- ✅ Road accessibility scores & zero accessibility on closure
- ✅ ML Random Forest risk probability within $[0, 1]$ bounds
- ✅ Multilingual intent detection & response generation
- ✅ FastAPI REST endpoints (`/api/chat`, `/api/routing/plan`, `/api/incidents`, `/api/digital-twin/*`)
- ✅ Disruption simulation & dynamic rerouting calculation
