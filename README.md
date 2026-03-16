# Trippy 3.0 — Production Multi-City AI Trip Planner

A production-grade multi-city journey planner using **9 LangGraph agents**, **11 live API tools**, and **Arize Phoenix Cloud observability**. Every mock tool from v2.0 has been replaced with real APIs (Google Maps, Tavily, Passport Index). Deployed on Railway + Vercel with full cost management and parallel agent execution.

**Part of a 3-project series:** See [Trippy v1](https://github.com/kkotecha/trippy) (foundations) and [Trippy 2.0](https://github.com/kkotecha/trippy2.0) (prototype with tool abstraction).

## Why This Version Exists

v1 proved agent decomposition. v2.0 built the multi-city architecture with a tool abstraction layer. v3.0 answers the production question: **What does it take to ship a multi-agent AI product with real data, real costs, and real observability?**

This version replaces every mock tool with live APIs, deploys to cloud infrastructure, introduces parallel agent execution, and deals with the production realities that separate prototypes from products: API cost management, rate limiting, CORS, error handling, and observability at scale.

## What Changed from v2.0

| Aspect | v2.0 | v3.0 |
|--------|------|------|
| Hotel data | Mock ("City Central Hotel") | **Google Places API** (real hotels, ratings, prices) |
| Attractions | 4 generic per city | **Google Places API** (real, interest-based) |
| Transport | 3 hardcoded routes | **Google Directions API** (real routes) |
| Visa info | 4 countries | **Passport Index API** (all countries) |
| Currency | 4 hardcoded | **RestCountries + ExchangeRate-API** (live rates) |
| Restaurants | None | **Google Places API** (real recommendations) |
| Execution | Sequential only | **Parallel** (budget + logistics run simultaneously) |
| Deployment | Local only | **Railway** (backend) + **Vercel** (frontend) |
| Cost visibility | None | **Full cost breakdown** per trip across all APIs |

## Architecture

### 9 Agents, 11 Live Tools

| Agent | Purpose | Data Source | Tool |
|-------|---------|-------------|------|
| 1. Country Research | Destination intelligence | Tavily Search | `web_search` |
| 2. Route Planning | Optimal city ordering | Nominatim (OSM) | `optimize_route` |
| 3. Transport | Inter-city routes | Google Directions | `search_trains` |
| 4. Accommodation | Hotels per city | Google Places | `search_hotels` |
| 5. Itinerary | Daily activities + dining | Google Places | `search_attractions`, `get_restaurant_recommendations` |
| 6. Local Transport | Metro, taxis, bikes | Google Places + Tavily | `get_transit_system_info`, `search_taxi_apps`, `search_bike_rentals` |
| 7. Budget Compiler | Cost aggregation | Aggregates real data | — |
| 8. Logistics | Visa, currency, packing | Passport Index, RestCountries, ExchangeRate | `get_visa_requirements`, `get_currency_info` |
| 9. Compiler | Final structured JSON | Aggregates all outputs | — |

### Execution Flow with Parallel Agents

```
Country Research → Route Planning → Transport → City Processing (loop per city)
                                                        │
                                                        ├──→ Budget    ──┐
                                                        └──→ Logistics ──┼──→ Compiler → Response
                                                                         │
                                                            (parallel)───┘
```

**Performance:** 65-90 seconds for a 4-city, 14-day trip. Parallel execution of Budget + Logistics saves ~5-8 seconds per request.

## AI & LLM Concepts

### LangGraph in Production: Parallel Execution + Error Handling

v3.0 introduces production patterns that go beyond v2.0's architecture:

**Parallel agent execution:** Budget and Logistics agents are independent — neither needs the other's output. LangGraph runs them simultaneously, reducing total latency. The pattern: **identify independent nodes in your graph and declare them as parallel.** This is a product decision as much as an engineering one — the PM decides which agents are independent, the graph makes it happen.

**Error resilience:** With 11 external API calls per request, failures are inevitable. Each tool has error handling that returns graceful fallbacks — if Google Places is slow, the agent works with cached or partial data rather than failing the entire trip. The observability layer (Phoenix) captures these failures for debugging.

**Data quality filtering at the tool level:** Hotels are filtered to 3.0+ stars minimum. Attractions are matched to user interests. Restaurants are categorized by meal type. These aren't LLM decisions — they're **tool-level filters** that improve output quality before the LLM ever sees the data. This is a critical pattern: **use tools to pre-filter, use the LLM to reason and synthesize.**

### Mock→Real Migration: The Payoff

This repo is the "after" to v2.0's "before." Comparing the tool layers side-by-side:

```
v2.0: search_hotels("Tokyo") → returns hardcoded "City Central Hotel, $150"
v3.0: search_hotels("Tokyo") → calls Google Places API → returns real hotels with ratings, prices, photos
```

The function signature and return shape are identical. Agent code is unchanged. The LangGraph workflow is unchanged. Only the tool internals changed. **This is the payoff of v2.0's tool abstraction pattern** — and the reason you invest in clean interfaces early.

### API Cost Management: A Product Decision

When you're calling 6+ external APIs per request, cost management becomes a product decision, not just an engineering concern:

| Cost Component | Per Trip | At 100 trips/month | At 1,000 trips/month |
|---------------|----------|--------------------|--------------------|
| OpenAI (GPT-4o-mini) | ~$0.15 | $15 | $150 |
| Google Maps APIs | ~$0.05 | $5 (within $200 free credit) | $50 |
| Tavily Search | Free tier | Free (within 1K/month) | ~$50 |
| Arize Phoenix | Free tier | Free | $49+ |
| **Total API cost** | **~$0.20** | **~$20** | **~$250+** |

`LANGCHAIN_PRICING.md` in this repo breaks down cost per request across all APIs. The insight: **LLM token cost is only ~75% of total cost when you add real API tools.** The remaining 25% is data APIs — and that ratio shifts as you add more tools.

This directly informs product decisions: pricing, usage limits, which features are free vs. premium, and where to invest in caching.

### Arize Phoenix Cloud: Production Observability

With 9 agents and 11 tools, observability isn't optional — it's the primary way you understand what your AI product is doing.

**What Phoenix Cloud captures per request:**
- Full agent execution trace: 9 agents, timing, token usage, state at each step
- Every tool call: arguments, responses, latency, errors
- LLM interactions: complete prompts, responses, token counts, model used
- End-to-end metrics: total latency, total tokens, total cost

**Production observability use cases:**

*Debugging:* "Why did the Japan trip take 90 seconds?" → Open the trace, find that Google Places timed out for Kyoto attractions, adding 25 seconds of retry time.

*Cost optimization:* "Which agent consumes the most tokens?" → Phoenix shows the Itinerary Agent uses ~40% of tokens because it generates detailed day-by-day plans for each city. Consider using a cheaper model for the Compiler Agent (which just formats JSON).

*Quality evaluation:* "Are our hotel recommendations good?" → Export the last 100 hotel tool responses from Phoenix, evaluate against user feedback. This is the dataset for prompt tuning.

**Phoenix platform capabilities for production AI:**

Beyond tracing, Phoenix Cloud provides the infrastructure for systematic AI improvement:

- **Experiments:** Run the same 50 trip requests through two different prompt variants for the Itinerary Agent. Compare outputs side-by-side with automated evaluation metrics. This replaces "I think prompt B is better" with data.

- **Evaluations:** Define quality criteria — "itinerary covers all stated user interests", "budget estimate within 20% of reality", "no hallucinated hotel names" — and run automated checks on every agent output. This is your AI quality gate.

- **Datasets:** Capture real user trip requests as a golden test suite. Every time you change a prompt, model, or tool, run the suite and compare. This prevents regressions — the AI equivalent of unit tests.

- **A/B Testing:** Route a percentage of production traffic through a new agent configuration (different model, different prompts, different tool) and compare quality metrics. This is how you iterate on AI products without guessing.

## Tech Stack

| Layer | Technology | Role |
|-------|-----------|------|
| Agent Orchestration | **LangGraph** + LangChain | 9-agent state machine with parallel execution |
| LLM | **OpenAI GPT-4o-mini** | Language model for all agents |
| Travel Data | **Google Maps** (Places + Directions), **Tavily**, **Passport Index**, RestCountries, ExchangeRate-API | 11 live tools grounding agents in real data |
| AI Observability | **Arize Phoenix Cloud** | Production tracing, cost attribution, team debugging |
| Backend | FastAPI + Uvicorn | API server |
| Frontend | HTML, Tailwind CSS, Vanilla JS | Multi-city planner UI |
| Deployment | **Railway** (backend) + **Vercel** (frontend) | Cloud infrastructure |

## Key Concepts Explored

**1. Mock→Real Migration: The Architecture Payoff**
Comparing v2.0 and v3.0 tool layers side-by-side demonstrates the value of clean tool abstraction. The function signatures are identical. Agent code is unchanged. Only tool internals changed. **This is the pattern for any AI product with external dependencies** — design for the data shape, not the API.

**2. Cost Management as Product Strategy**
`LANGCHAIN_PRICING.md` breaks down per-request cost across all APIs. When you're calling 6+ external APIs per request, understanding cost at the tool level — not just LLM token cost — becomes a product decision that informs pricing, feature gating, and architecture.

**3. Parallel Agent Execution**
Budget and Logistics agents run simultaneously since they're independent. Saves ~5-8 seconds per request. The pattern: **identify independent nodes in your graph and run them in parallel.** This is a product decision — the PM identifies which steps are independent, the engineer declares them parallel in the graph.

**4. Data Quality at the Tool Level**
Hotels filtered to 3.0+ stars. Attractions matched to user interests. Restaurants categorized by meal type. These are tool-level decisions that improve quality before the LLM reasons over the data. **Pre-filter with tools, synthesize with the LLM.**

**5. Production Observability with Phoenix Cloud**
With 9 agents and 11 tools, the trace visualization shows exactly where time is spent, which APIs are slow, where errors occur, and what each agent costs. This is the foundation for systematic AI improvement — experiments, evaluations, and A/B testing all build on the tracing layer.

## Getting Started

### Prerequisites
- Python 3.9+
- OpenAI API key (required)
- Google Maps API key (required — enable Places API + Directions API)
- Tavily API key (required for web search)
- Arize Phoenix account (optional, for cloud observability)

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
# Add: ARIZE_SPACE_ID + ARIZE_API_KEY (optional, for Phoenix Cloud)
```

**Getting API Keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Google Maps**: https://console.cloud.google.com/apis (enable Places + Directions)
- **Tavily**: https://tavily.com (free tier: 1,000 searches/month)
- **Arize Phoenix**: https://app.arize.com (free tier available)

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

This is the production version. If you're starting from scratch, begin with [v1](https://github.com/kkotecha/trippy) for the fundamentals. If you're here to understand what production multi-agent AI looks like, read on.

**Step 1: Compare tools between v2.0 and v3.0**
Open `backend/tools/hotel_tools.py` in both repos side by side. In v2.0 it returns hardcoded data. In v3.0 it calls Google Places API. The function signature and return shape are identical. **This is the payoff of the tool abstraction pattern** — and the most reusable lesson from this series.

**Step 2: Trace a full request in Phoenix Cloud**
Set up Arize credentials and plan a 4-city trip. Open the trace in Phoenix Cloud — with 9 agents and 11 tools, the visualization shows the complete execution flow. Find the parallel branch (Budget + Logistics). Identify the slowest tool call. Calculate token cost per agent. **This is how you build a mental model for production AI systems.**

**Step 3: Read the cost analysis**
`LANGCHAIN_PRICING.md` breaks down cost per trip across all APIs. Build a mental model for how API costs compound in multi-tool systems — this directly informs product pricing and architecture decisions. Notice that LLM cost isn't the whole story — data APIs add significant cost that scales differently.

**Step 4: Study the deployment stack**
Read `Procfile`, `vercel.json`, `start.sh`, and the CORS configuration in `main.py`. These are the unglamorous files every real deployment needs. The gap between "works locally" and "deployed and accessible" is mostly these files.

**Step 5: Run an experiment (advanced)**
Using Phoenix Cloud, capture 10 trip requests as a dataset. Modify the Itinerary Agent's system prompt (e.g., add "include estimated walking time between activities"). Re-run the same 10 requests. Compare the outputs in Phoenix — did the change improve quality? Increase token cost? This is the **experiment-driven approach to AI product development** that Phoenix enables.

**Step 6: Deploy your own instance**
Follow `DEPLOYMENT.md` to deploy to Railway + Vercel. The experience of configuring environment variables, debugging CORS, and handling cold starts is valuable real-world knowledge that tutorials rarely cover.

## Project Structure

```
trippy3.0/
├── backend/
│   ├── main.py                        # FastAPI entry point
│   ├── config.py                      # Environment config
│   ├── observability.py               # Arize Phoenix Cloud setup
│   ├── agents/                        # 9 specialized LangGraph agents
│   │   ├── country_research.py        # Tavily search (real data)
│   │   ├── route_planning.py          # Geopy/OSM geocoding
│   │   ├── transport.py               # Google Directions API
│   │   ├── city_processing.py         # Google Places (hotels, attractions, dining)
│   │   ├── budget.py                  # Cost aggregation from real data
│   │   ├── logistics.py               # Passport Index, RestCountries, ExchangeRate
│   │   └── compiler.py                # Final JSON builder
│   ├── tools/                         # 11 live API tool implementations
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
├── start.sh                           # Backend startup script
├── DEPLOYMENT.md                      # Deployment guide
├── LANGCHAIN_PRICING.md               # API cost analysis per trip
└── README.md
```

## The Trippy Series

This series demonstrates the full lifecycle of building a multi-agent AI product — from first prototype to production deployment.

| Version | Focus | Agents | Data | Observability |
|---------|-------|--------|------|---------------|
| [**v1**](https://github.com/kkotecha/trippy) | Agent decomposition, LangGraph basics | 4 | LLM-only | Phoenix local |
| [**v2.0**](https://github.com/kkotecha/trippy2.0) | Multi-city, tool abstraction, mock→real path | 9 | Mixed (2 real + 5 mock) | Phoenix Cloud |
| **v3.0 (this repo)** | Production — real APIs, parallel execution, cost management | 9 | All real (11 live tools) | Phoenix Cloud |

**The progression tells a product story:**
1. **v1**: Can specialized agents outperform a single prompt? (Yes — and Phoenix proves it.)
2. **v2.0**: Can we scale with a clean tool layer and make every agent decision observable?
3. **v3.0**: Can we ship it with real data, real deployment, and cost management that makes business sense?

Each version builds on the previous one's patterns while introducing new production concerns. The series is designed to be read and built in order — each step adds complexity that the previous step's architecture supports.

## License

MIT
