# Multi-City Trip Planner 🌍

AI-powered country journey planner using LangGraph's multi-agent architecture with Arize Phoenix Cloud observability.

> ✅ **Project Status:** Fully functional with **real dynamic data** from Google Places, Google Directions, and free public APIs. All critical travel planning tools now use live data!

## Features

- 🗺️ **Multi-city route optimization** - Plan journeys across 2-6 cities with intelligent routing
- 🚆 **Inter-city transportation** - Real train/transit routes via Google Directions API
- 🏨 **Accommodation recommendations** - Real hotels from Google Places (≥3.0 stars only)
- 📅 **Day-by-day itineraries** - Real attractions based on your interests via Google Places
- 🍽️ **Restaurant recommendations** - Dynamic meal suggestions for breakfast, lunch, dinner
- 🚇 **Local transportation** - City-specific metro, taxi apps, bike rentals
- 💰 **Budget breakdowns** - Complete cost estimates with real pricing data
- 🎒 **Travel logistics** - Visa requirements (all nationalities), currency info, packing lists
- 🔍 **Full observability** - Arize Phoenix Cloud tracing of all agents and LLM calls
- ⚡ **Parallel processing** - Budget and logistics agents run simultaneously for faster responses

## Architecture

### 9 Specialized Agents (All Fully Dynamic)

| Agent | Purpose | Data Source | Status |
|-------|---------|-------------|--------|
| 1. **Country Research Agent** | Destination intelligence, visa, currency info | Tavily Search, Passport Index, RestCountries | ✅ Dynamic |
| 2. **Route Planning Agent** | Optimal city ordering and route optimization | Nominatim (OSM) geocoding | ✅ Dynamic |
| 3. **Transport Agent** | Inter-city travel options (trains/buses) | Google Directions API | ✅ Dynamic |
| 4. **Accommodation Agent** | Hotel/hostel recommendations per city | Google Places API | ✅ Dynamic |
| 5. **Itinerary Agent** | Daily activities, attractions, restaurants | Google Places API | ✅ Dynamic |
| 6. **Local Transport Agent** | Metro systems, taxi apps, bike rentals | Google Places + Tavily Search | ✅ Dynamic |
| 7. **Budget Compiler** | Financial breakdown and cost estimates | Aggregates real data | ✅ Dynamic |
| 8. **Logistics Agent** | Packing lists, visas, currency, health tips | Passport Index, RestCountries | ✅ Dynamic |
| 9. **Compiler Agent** | Final structured JSON response | Aggregates all agent outputs | ✅ Dynamic |

**Execution Model:** Sequential pipeline with parallel budget/logistics processing for optimal performance.

### Tool Status: All Tools Now Dynamic! ✅

| Tool | Description | Data Source | Quality |
|------|-------------|-------------|---------|
| `web_search` | Real-time web search | **Tavily API** | ✅ Live data |
| `search_hotels` | Hotel recommendations | **Google Places API** | ✅ Real hotels (≥3.0⭐) |
| `search_trains` | Train/transit routes | **Google Directions API** | ✅ Real routes |
| `search_attractions` | Tourist attractions | **Google Places API** | ✅ Real attractions |
| `get_restaurant_recommendations` | Meal recommendations | **Google Places API** | ✅ Real restaurants |
| `get_transit_system_info` | Metro/subway systems | **Google Places API** | ✅ Real transit |
| `search_taxi_apps` | Ride-sharing apps | **Tavily Search** | ✅ City-specific |
| `search_bike_rentals` | Bike sharing | **Tavily Search** | ✅ City-specific |
| `get_visa_requirements` | Visa information | **Passport Index API** | ✅ All countries |
| `get_currency_info` | Currency & exchange rates | **RestCountries + ExchangeRate-API** | ✅ Live rates |
| `optimize_route` | City route optimization | **Nominatim (OSM)** | ✅ Real geocoding |

**Cost:** All within free tier limits (~200-900 trips/month capacity)

> 📋 **See [TOOL_IMPROVEMENT_ANALYSIS.md](backend/TOOL_IMPROVEMENT_ANALYSIS.md)** for detailed implementation notes and API documentation.

## Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key (required)
- Google Maps API key (required for hotels, attractions, transport)
- Tavily API key (required for web search)
- Arize Phoenix account (optional, for cloud observability)

### Installation

```bash
# Clone repository
cd trippy2.0

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your keys:
#   - OPENAI_API_KEY (required)
#   - TAVILY_API_KEY (optional but recommended)
#   - ARIZE_SPACE_ID and ARIZE_API_KEY (optional)
```

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Required - LLM
OPENAI_API_KEY=sk-your-openai-api-key

# Required - Travel Data APIs
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
TAVILY_API_KEY=tvly-your-tavily-api-key

# Optional - Arize Phoenix Cloud Observability
ARIZE_SPACE_ID=your-space-id
ARIZE_API_KEY=your-api-key
ARIZE_PROJECT_NAME=trippy-multi-city

# App Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.5
```

**Getting API Keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Google Maps**: https://console.cloud.google.com/apis (Enable Places API & Directions API)
- **Tavily**: https://tavily.com (Free tier: 1,000 searches/month)
- **Arize Phoenix**: https://app.arize.com (Optional, for observability)

### Running the Application

```bash
# Terminal 1: Run backend
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

Backend runs at:
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs (Interactive Swagger UI)
- **Arize Phoenix:** https://app.arize.com (if configured)

```bash
# Terminal 2: Run frontend
cd frontend
python3 -m http.server 3000
```

Visit: **http://localhost:3000**

## Usage Example

### Input:
```json
{
  "nationality": "India",
  "country": "Japan",
  "total_duration": 14,
  "interests": ["temples", "food", "technology"],
  "budget_tier": "moderate",
  "starting_city": "Tokyo",
  "travel_pace": "moderate",
  "num_cities": 4
}
```

### Output:
```json
{
  "country_overview": "Detailed Japan overview...",
  "city_route": ["Tokyo", "Kyoto", "Osaka", "Hiroshima"],
  "nights_per_city": {
    "Tokyo": 4,
    "Kyoto": 4,
    "Osaka": 3,
    "Hiroshima": 3
  },
  "transport_legs": [
    {
      "from": "Tokyo",
      "to": "Kyoto",
      "method": "Shinkansen (bullet train)",
      "duration": "2h 15min",
      "cost": "$130"
    }
  ],
  "city_plans": [
    {
      "city_name": "Tokyo",
      "nights": 4,
      "accommodation": [
        {
          "name": "Hotel Gracery Shinjuku",
          "rating": 4.2,
          "price_per_night": "$120",
          "booking_link": "https://www.google.com/maps/place/?q=place_id:..."
        }
      ],
      "itinerary": [
        {
          "day": 1,
          "activities": [
            {
              "time": "09:00",
              "activity": "Senso-ji Temple",
              "location": "2 Chome-3-1 Asakusa, Taito City",
              "cost": "$5"
            }
          ],
          "meals": {
            "breakfast": "Tsukiji Outer Market Café ($12)",
            "lunch": "Ichiran Ramen Shibuya ($15)",
            "dinner": "Gonpachi Nishiazabu ($40)"
          }
        }
      ],
      "local_transport": {
        "metro_system": "Tokyo Metro",
        "day_pass_cost": "$10",
        "taxi_apps": ["Uber", "Lyft", "Grab"],
        "bike_rentals": "Lime, Bird"
      }
    }
  ],
  "total_budget_estimate": 3500,
  "budget_breakdown": {...},
  "packing_list": [...],
  "travel_logistics": {
    "visa_requirements": "✅ Visa-free for Indian citizens for 90 days",
    "currency": {
      "code": "JPY",
      "exchange_rate": "1 USD = 147.09 JPY"
    }
  }
}
```

> ✅ **All data above is real** - hotels, restaurants, attractions, and transport from live APIs!

## Observability with Arize Phoenix Cloud

This project includes full observability using **Arize Phoenix Cloud** to trace:
- All 9 agent executions
- LLM calls with prompts and responses
- Tool invocations and results
- Token usage and costs
- Execution timeline and dependencies

### Setup Arize Phoenix

1. **Sign up** at https://app.arize.com
2. **Create a project** or use existing space
3. **Get credentials:**
   - Space ID from space settings
   - API Key from space settings
4. **Add to `.env`:**
   ```bash
   ARIZE_SPACE_ID=your-space-id
   ARIZE_API_KEY=your-api-key
   ARIZE_PROJECT_NAME=trippy-multi-city
   ```
5. **Restart backend** - traces will appear in Arize dashboard

### What You'll See in Phoenix

- 🔍 Complete agent workflow graph
- 📊 LLM token usage and costs
- ⏱️ Performance bottlenecks
- 🛠️ Tool success/failure rates
- 🔗 Full trace of each request through all 9 agents

View traces at: **https://app.arize.com**

## Project Structure

```
trippy2.0/
├── README.md                          # This file
├── backend/
│   ├── main.py                        # FastAPI application entry point
│   ├── config.py                      # Configuration and environment variables
│   ├── observability.py               # Arize Phoenix Cloud setup
│   ├── requirements.txt               # Python dependencies
│   ├── TOOL_IMPROVEMENT_ANALYSIS.md   # Detailed tool improvement roadmap
│   │
│   ├── agents/                        # 9 specialized agents
│   │   ├── country_research.py        # Agent 1: Destination intelligence
│   │   ├── route_planning.py          # Agent 2: City route optimization
│   │   ├── transport.py               # Agent 3: Inter-city transport
│   │   ├── accommodation.py           # Agent 4: Hotels per city
│   │   ├── itinerary.py               # Agent 5: Daily activities per city
│   │   ├── local_transport.py         # Agent 6: Getting around cities
│   │   ├── budget.py                  # Agent 7: Cost compilation
│   │   ├── logistics.py               # Agent 8: Packing and prep
│   │   └── compiler.py                # Agent 9: Final response builder
│   │
│   ├── tools/                         # Tool implementations
│   │   ├── __init__.py                # Tool exports
│   │   ├── search_tools.py            # ✅ web_search (Tavily API)
│   │   ├── calculation_tools.py       # ✅ optimize_route, calculate_travel_time
│   │   ├── hotel_tools.py             # ✅ search_hotels (Google Places API)
│   │   ├── transport_tools.py         # ✅ search_trains (Google Directions API)
│   │   ├── attraction_tools.py        # ✅ search_attractions (Google Places API)
│   │   └── knowledge_tools.py         # ✅ visa/currency (Passport Index, RestCountries)
│   │
│   └── graph/                         # LangGraph workflow
│       ├── state.py                   # State definitions (TripPlannerState, CityState)
│       └── workflow.py                # Agent orchestration graph
│
└── frontend/
    ├── index.html                     # Trip planner form UI
    ├── script.js                      # API calls and result rendering
    └── style.css                      # Styling
```

## Development

### Adding a New Tool

1. Create tool in `backend/tools/your_tool.py`:

```python
from langchain_core.tools import tool

@tool
def your_new_tool(param: str) -> dict:
    """
    Tool description that the LLM will see.
    Be specific about what it does and when to use it.
    """
    # Implementation with error handling
    try:
        result = your_api_call(param)
        return {"data": result}
    except Exception as e:
        return {"error": str(e)}
```

2. Export in `backend/tools/__init__.py`
3. Import and use in relevant agent

### Adding a New Agent

1. Create agent in `backend/agents/your_agent.py`:

```python
from graph.state import TripPlannerState
from langchain_openai import ChatOpenAI
from tools import your_tool

def your_agent_node(state: TripPlannerState) -> dict:
    """Agent implementation with LLM and tools"""
    llm = ChatOpenAI(model="gpt-4o-mini")

    # Use tools and LLM to process state
    result = your_tool.invoke({"param": state["field"]})

    return {"new_field": result}
```

2. Update `backend/graph/state.py` to add new state fields
3. Add node to workflow in `backend/graph/workflow.py`

### Upgrading Mock Tools to Real APIs

See **[TOOL_IMPROVEMENT_ANALYSIS.md](backend/TOOL_IMPROVEMENT_ANALYSIS.md)** for:
- Detailed analysis of each mock tool
- Recommended APIs with links
- Implementation priorities
- Cost considerations
- Code examples

**Priority order:**
1. `search_hotels` → Booking.com API or Google Places
2. `search_attractions` → Google Places or TripAdvisor
3. `search_trains` → Rome2Rio or Trainline API

## Troubleshooting

### Backend won't start

```bash
# Ensure you're in venv
cd backend
source venv/bin/activate

# Check dependencies
pip install -r requirements.txt

# Verify .env file exists and has OPENAI_API_KEY
cat .env
```

### Arize Phoenix Cloud not connecting

```bash
# Check credentials in .env
ARIZE_SPACE_ID=...  # Should be base64 encoded string
ARIZE_API_KEY=...   # Should start with "ak-"

# Verify credentials at https://app.arize.com space settings
# Check backend logs for connection errors
```

### Tool errors during execution

- Check `.env` has all required API keys
- Verify network connection
- Check Arize Phoenix dashboard for detailed error traces
- Look at backend console logs for specific tool failures

### Slow responses

- **Expected:** 60-90 seconds for full multi-city journey
- **Normal bottlenecks:**
  - Country research (web search): 5-10s
  - Each city itinerary planning: 8-12s per city
  - Route optimization with 4+ cities: 5-8s
- **Check:** Arize Phoenix timeline view to identify slow agents
- **Optimization:** Consider using `gpt-4o-mini` (current) vs `gpt-4` for speed

## API Response Times

Typical execution breakdown for 4-city, 14-day trip:

| Agent | Time | Reason |
|-------|------|--------|
| Country Research | 10-15s | Web search + LLM processing |
| Route Planning | 5-8s | Geocoding + optimization |
| Transport | 3-5s | Mock data lookup |
| City Planning (×4) | 40-50s | LLM generates itinerary per city |
| Budget | 3-5s | Aggregation |
| Logistics | 3-5s | Packing list generation |
| Compiler | 2-3s | JSON assembly |
| **Total** | **65-90s** | End-to-end |

## Roadmap

### ✅ Phase 1: Dynamic Data (COMPLETED)
- [x] Integrate Google Places API for hotels, attractions, restaurants
- [x] Implement Google Directions API for transport routes
- [x] Add Passport Index API for visa requirements
- [x] Integrate RestCountries + ExchangeRate-API for currency
- [x] Hybrid local transport (Google Places + web search)
- [x] Parallel agent execution (budget + logistics)
- [x] Minimum hotel quality filter (≥3.0 stars)
- [x] Dynamic rating verbiage

### Phase 2: Enhanced Features (In Progress)
- [ ] Interactive map visualization with route overlay
- [ ] PDF export of complete itinerary
- [ ] Save/load trip plans (local storage)
- [ ] User authentication and trip history
- [ ] Real-time pricing from booking APIs
- [ ] Weather forecasts for travel dates
- [ ] Flight search integration

### Phase 3: Advanced Features
- [ ] Direct booking integration (hotels/trains)
- [ ] Multi-country trips (e.g., Thailand + Vietnam)
- [ ] Collaborative trip planning (multiple users)
- [ ] Mobile app with offline itinerary access
- [ ] AI-powered trip modifications ("Add one more day in Kyoto")
- [ ] Budget tracking during trip
- [ ] Photo recommendations from Instagram/Pinterest

## Contributing

Contributions welcome! Priority areas:
1. **Frontend improvements** - Map view, better visualizations, PDF export
2. **Performance optimization** - Caching, parallel city processing
3. **Testing** - Unit tests for agents and tools
4. **New features** - Multi-country trips, booking integration

## Known Limitations

⚠️ **Pricing:**
- Hotel and attraction prices are estimates (Google doesn't provide real-time pricing)
- Train costs estimated based on distance formulas
- For actual booking prices, use the provided Google Maps/Rome2Rio/Omio links

⚠️ **Performance:**
- 60-90 second response time for full trip plans
- Rate limited by Nominatim geocoding (1 req/sec)
- Tavily free tier limits to ~200-300 trips/month

⚠️ **Functionality:**
- No user authentication or data persistence
- Cannot modify generated plans (must regenerate)
- Limited to single-country trips
- Max 6 cities per trip
- Google Maps API free tier limits (~900 trips/month)

## License

MIT License - feel free to use and modify for your own projects.

## Credits

Built with:
- **[LangGraph](https://github.com/langchain-ai/langgraph)** - Multi-agent orchestration
- **[LangChain](https://github.com/langchain-ai/langchain)** - LLM framework
- **[Arize Phoenix](https://phoenix.arize.com/)** - AI observability platform
- **[FastAPI](https://fastapi.tiangolo.com/)** - Backend framework
- **[OpenAI GPT-4o-mini](https://openai.com/)** - Language model
- **[Google Maps Platform](https://developers.google.com/maps)** - Places & Directions APIs
- **[Tavily](https://tavily.com/)** - Web search API
- **[Passport Index](https://www.passportindex.org/)** - Visa requirements API
- **[RestCountries](https://restcountries.com/)** - Country data API
- **[ExchangeRate-API](https://www.exchangerate-api.com/)** - Currency exchange rates
- **[Geopy](https://geopy.readthedocs.io/)** - Geocoding and route optimization

---

**Last Updated:** October 3, 2025
**Version:** 3.0.0 (Production-Ready with Dynamic Data)
