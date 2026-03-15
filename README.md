# Trippy 3.0 — Production Multi-City AI Trip Planner

An AI-powered multi-city journey planner using 9 LangGraph agents with fully dynamic data from Google Maps, Tavily, Passport Index, and other live APIs. Deployed on Railway + Vercel.

**Part of a 3-project series:** See [Trippy v1](https://github.com/kkotecha/trippy) (foundations) and [Trippy 2.0](https://github.com/kkotecha/trippy2.0) (prototype with mock data).

## Why This Version Exists

v1 proved agent decomposition. v2.0 built the multi-city architecture with a mock tool layer. v3.0 answers the final question: **What does it take to go from working prototype to deployed product with real data?**

This version replaces every mock tool with live APIs, deploys to cloud infrastructure, and deals with production realities: CORS, rate limits, API costs, error handling, and observability at scale.

## What Changed from v2.0

| Aspect | v2.0 | v3.0 |
|--------|------|------|
| Hotel data | Mock ("City Central Hotel") | Google Places API (real hotels, ratings, prices) |
| Attractions | 4 generic per city | Google Places API (real, interest-based) |
| Transport | 3 hardcoded routes | Google Directions API (real routes) |
| Visa info | 4 countries | Passport Index API (all countries) |
| Currency | 4 hardcoded | RestCountries + ExchangeRate-API (live rates) |
| Restaurants | None | Google Places API (real recommendations) |
| Deployment | Local only | Railway (backend) + Vercel (frontend) |
| Processing | Sequential only | Parallel (budget + logistics run simultaneously) |

## Architecture

### 9 Agents — All Fully Dynamic

| Agent | Purpose | Data Source |
|-------|---------|-------------|
| 1. Country Research | Destination intelligence | Tavily Search |
| 2. Route Planning | Optimal city ordering | Nominatim (OSM) geocoding |
| 3. Transport | Inter-city routes | Google Directions API |
| 4. Accommodation | Hotels per city | Google Places API |
| 5. Itinerary | Daily activities + restaurants | Google Places API |
| 6. Local Transport | Metro, taxis, bikes | Google Places + Tavily |
| 7. Budget Compiler | Cost aggregation | Aggregates real data |
| 8. Logistics | Visa, currency, packing | Passport Index, RestCountries, ExchangeRate-API |
| 9. Compiler | Final JSON | Aggregates all outputs |

### Execution Flow

```
Country Research → Route Planning → Transport → City Processing (loop per city)
                                                        │
                                                        ├──→ Budget    ──┐
                                                        └──→ Logistics ──┼──→ Compiler → Response
                                                                         │
                                                            (parallel)───┘
```

**Performance:** 65-90 seconds for a 4-city, 14-day trip.

### 11 Live Tools

| Tool | API | What It Returns |
|------|-----|----------------|
| `web_search` | Tavily | Current destination info |
| `search_hotels` | Google Places | Real hotels with ratings, prices, links |
| `search_attractions` | Google Places | Interest-matched attractions |
| `get_restaurant_recommendations` | Google Places | Breakfast, lunch, dinner spots |
| `search_trains` | Google Directions | Train/transit routes with durations |
| `get_transit_system_info` | Google Places | Metro/subway systems |
| `search_taxi_apps` | Tavily | City-specific ride-sharing apps |
| `search_bike_rentals` | Tavily | Bike sharing options |
| `get_visa_requirements` | Passport Index | Visa needs for any nationality |
| `get_currency_info` | RestCountries + ExchangeRate | Live exchange rates |
| `optimize_route` | Nominatim (OSM) | City ordering via TSP |

All tools operate within free API tiers (~200-900 trips/month capacity).

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Uvicorn |
| Agent Orchestration | LangGraph + LangChain |
| LLM | OpenAI GPT-4o-mini |
| Travel Data | Google Maps (Places + Directions), Tavily, Passport Index, RestCountries, ExchangeRate-API |
| Observability | Arize Phoenix Cloud |
| Frontend | HTML, Tailwind CSS, Vanilla JS |
| Deployment | Railway (backend), Vercel (frontend) |

## Key Concepts Explored

**1. Mock → Real API Migration**
This repo is the "after" to v2.0's "before." Comparing the two tool layers shows how a clean abstraction lets you swap data sources without touching agent logic. The key insight: **design your tool interfaces around the data shape you need, not the API you're calling.**

**2. Production Deployment Concerns**
Local development hides a lot: CORS, environment-specific config, startup scripts, health checks. The `Procfile`, `vercel.json`, `start.sh`, and CORS middleware in `main.py` are worth studying — these are the unglamorous files that make deployment work.

**3. API Cost Management**
`LANGCHAIN_PRICING.md` breaks down the per-request cost across all APIs. When you're calling 6+ external APIs per request, understanding cost at the tool level (not just LLM token cost) becomes a product decision.

**4. Parallel Agent Execution**
Budget and logistics agents run simultaneously since they're independent. This reduces total response time by ~5-8 seconds. The pattern: identify independent nodes in your graph and run them in parallel.

**5. Data Quality Filtering**
Hotels are filtered to 3.0+ stars minimum. Attractions are matched to user interests. These aren't LLM decisions — they're tool-level filters that improve output quality before the LLM ever sees the data.

## Getting Started

### Prerequisites
- Python 3.9+
- OpenAI API key (required)
- Google Maps API key (required — enable Places API + Directions API)
- Tavily API key (required for web search)
- Arize Phoenix account (optional, for observability)

### Setup

```bash
git clone https://github.com/kkotecha/trippy3.0.git
cd trippy3.0

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add: OPENAI_API_KEY, GOOGLE_MAPS_API_KEY, TAVILY_API_KEY
```

**Getting API Keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Google Maps**: https://console.cloud.google.com/apis (enable Places + Directions)
- **Tavily**: https://tavily.com (free tier: 1,000 searches/month)

```bash
# Run backend
python main.py
# API at http://localhost:8000, Swagger docs at http://localhost:8000/docs

# Frontend (separate terminal)
cd frontend
python3 -m http.server 3000
# Visit http://localhost:3000
```

## For Practitioners: How to Use This Repo

If you've followed the series from v1, this is where everything comes together. If you're starting here, consider reviewing [v1](https://github.com/kkotecha/trippy) first for the fundamentals.

**Step 1: Compare tools between v2.0 and v3.0**
Open `backend/tools/hotel_tools.py` in both repos side by side. In v2.0 it returns hardcoded data. In v3.0 it calls Google Places API. Notice: the function signature and return shape are identical. This is the payoff of the tool abstraction pattern.

**Step 2: Study the deployment files**
Read `Procfile`, `vercel.json`, `start.sh`, and the CORS configuration in `main.py`. These are the files most tutorials skip but every real deployment needs.

**Step 3: Run with Arize Phoenix**
Set up Arize credentials and trace a full request. With 9 agents and 11 tools, the trace visualization shows you exactly where time is spent, which APIs are slow, and where errors occur. This is production-grade observability.

**Step 4: Read the cost analysis**
`LANGCHAIN_PRICING.md` breaks down cost per trip across all APIs. Build a mental model for how API costs compound in multi-tool systems — this directly informs product pricing and architecture decisions.

**Step 5: Deploy your own instance**
Follow `DEPLOYMENT.md` to deploy to Railway + Vercel. The experience of configuring environment variables, debugging CORS, and handling cold starts is valuable real-world knowledge.

## Project Structure

```
trippy3.0/
├── backend/
│   ├── main.py                        # FastAPI entry point
│   ├── config.py                      # Environment config
│   ├── observability.py               # Arize Phoenix Cloud
│   ├── agents/                        # 9 specialized agents
│   │   ├── country_research.py        # Tavily search
│   │   ├── route_planning.py          # Geopy/OSM geocoding
│   │   ├── transport.py               # Google Directions
│   │   ├── city_processing.py         # Google Places (hotels, attractions, food)
│   │   ├── budget.py                  # Cost aggregation
│   │   ├── logistics.py               # Passport Index, RestCountries
│   │   └── compiler.py                # Final JSON builder
│   ├── tools/                         # All real API implementations
│   │   ├── search_tools.py            # Tavily web search
│   │   ├── hotel_tools.py             # Google Places (hotels)
│   │   ├── attraction_tools.py        # Google Places (attractions)
│   │   ├── transport_tools.py         # Google Directions
│   │   ├── knowledge_tools.py         # Passport Index + RestCountries + ExchangeRate
│   │   └── calculation_tools.py       # Geopy route optimization
│   └── graph/
│       ├── state.py                   # TripPlannerState + CityState
│       └── workflow.py                # LangGraph workflow with parallel nodes
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── env-config.js                  # Environment-aware API URL
├── Procfile                           # Railway deployment
├── vercel.json                        # Vercel frontend config
├── DEPLOYMENT.md                      # Deployment guide
├── LANGCHAIN_PRICING.md               # API cost analysis
└── README.md
```

## The Trippy Series

This series demonstrates the full lifecycle of building a multi-agent AI product — from concept to production.

| Version | Focus | Agents | Data Sources | Status |
|---------|-------|--------|-------------|--------|
| [**v1**](https://github.com/kkotecha/trippy) | Foundations — agent decomposition, LangGraph basics | 4 | LLM-only | Prototype |
| [**v2.0**](https://github.com/kkotecha/trippy2.0) | Scale — multi-city, tools, mock data layer | 9 | Mixed (real + mock) | Prototype |
| **v3.0 (this repo)** | Production — real APIs, deployment, observability | 9 | All real (Google Maps, Tavily, etc.) | Deployed |

**The progression tells a story:**
1. **v1**: Can we decompose a complex task into specialized agents?
2. **v2.0**: Can we scale to multi-city with a clean tool abstraction?
3. **v3.0**: Can we ship it with real data, real deployment, and real cost management?

Each version builds on the previous one's patterns while introducing new production concerns.

## License

MIT
