# Tool Improvement Analysis - Multi-City Trip Planner

This document analyzes all tools in the system and identifies which ones are static/dummy vs dynamic, with recommendations for making them more powerful.

---

## ✅ DYNAMIC TOOLS (Working Well)

### 1. `web_search` (search_tools.py)
**Current Behavior:** Uses Tavily API to search the web for real-time information
**Status:** ✅ Fully dynamic
**Why it works:** Makes actual API calls to Tavily search engine, returns real search results
**Recommendation:** No changes needed. This is a properly implemented dynamic tool.

---

### 2. `get_visa_requirements` (knowledge_tools.py) - **UPGRADED ✅**
**Status:** ✅ Fully dynamic (Recently implemented)
**Implementation:** Passport Index API (free, no auth)
**Details:** See section below for full implementation details.

---

### 3. `get_currency_info` (knowledge_tools.py) - **UPGRADED ✅**
**Status:** ✅ Fully dynamic (Recently implemented)
**Implementation:** RestCountries API + ExchangeRate-API (both free)
**Details:** See section below for full implementation details.

---

### 4. `optimize_route` (calculation_tools.py)
**Current Behavior:** Uses geopy/Nominatim to geocode cities and calculate optimal route using greedy nearest-neighbor algorithm
**Status:** ✅ Mostly dynamic
**Why it works:** Makes real API calls to OpenStreetMap's Nominatim service for geocoding, calculates real distances
**Recommendation:** Consider upgrading to TSP (Traveling Salesman Problem) solver for truly optimal routes instead of greedy algorithm. Libraries like `python-tsp` or Google OR-Tools would provide better optimization.

---

## ❌ STATIC/DUMMY TOOLS (Need Improvement)

### 5. `search_hotels` (hotel_tools.py) - **UPGRADED ✅**
**Status:** ✅ Fully dynamic (Recently implemented)
**Implementation:** Google Places API (free tier: $200/month credit)

**Current Behavior:** Uses Google Places Text Search API for real hotel data
```python
url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
params = {"query": f"{tier_keywords[budget_tier]} in {city}", "type": "lodging"}
```

**Why it works:**
- Fetches **real hotels** from Google Places database for any city worldwide
- Returns actual hotel names, addresses, and ratings from Google Maps
- Filters hotels with **rating ≥ 3.0 stars** only (quality control)
- Budget-tier specific queries ("budget hostel", "luxury boutique hotel")
- Links to **Google Maps business profiles** (not Booking.com)
- Dynamic verbiage based on rating:
  - 4.5+ stars: "Exceptional"
  - 4.0-4.4 stars: "Highly rated"
  - 3.5-3.9 stars: "Well-rated"
  - 3.0-3.4 stars: "Rated"
- Includes real review counts and addresses
- Falls back to mock data only if API fails

**Implementation Details:**
- API: Google Places Text Search
- Cost: Free tier ($200/month credit = ~900 trips/month)
- Quality filter: Only hotels with rating ≥ 3.0
- Link format: `https://www.google.com/maps/place/?q=place_id:{place_id}`
- No authentication required (uses GOOGLE_MAPS_API_KEY from .env)

**Recent Improvements:**
- ✅ Added 3.0 star minimum rating filter
- ✅ Replaced Booking.com links with Google Maps business profiles
- ✅ Dynamic rating descriptions (prevents "Highly rated (2.5 stars)")
- ✅ Real review counts displayed

---

### 6. `search_trains` (transport_tools.py) - **UPGRADED ✅**
**Status:** ✅ Fully dynamic (Recently implemented)
**Implementation:** Google Directions API with transit mode (free tier: $200/month credit)

**Current Behavior:** Uses Google Directions API for real train/transit routes
```python
url = "https://maps.googleapis.com/maps/api/directions/json"
params = {
    "origin": from_city,
    "destination": to_city,
    "mode": "transit",
    "transit_mode": "train|rail"
}
```

**Why it works:**
- Fetches **real train/transit routes** between any two cities worldwide
- Returns actual duration, distance, and transit details from Google
- Generates affiliate booking links to **Rome2Rio** and **Omio** for actual booking
- Works for any city pair globally (not limited to Japan/France)
- Estimates costs based on distance and country
- Includes transit provider names when available
- Falls back to mock data only if API fails

**Implementation Details:**
- API: Google Directions API (transit mode)
- Cost: Free tier ($200/month credit shared with Places API)
- Booking links: Rome2Rio + Omio affiliate URLs
- No authentication required (uses GOOGLE_MAPS_API_KEY from .env)

**Returned Data:**
- Actual duration (e.g., "2h 15m") from Google
- Real distance in km
- Estimated cost based on distance formula
- Transit provider details when available
- Clickable booking links to Rome2Rio and Omio

**Future Enhancements:**
- Add real-time pricing APIs (currently estimated)
- Include train schedules and departure times
- Add seat availability checking
- Support for train passes (JR Pass, Eurail, etc.)

---

### 7. `search_attractions` (attraction_tools.py) - **UPGRADED ✅**
**Status:** ✅ Fully dynamic (Recently implemented)
**Implementation:** Google Places API Text Search (free tier: $200/month credit)

**Current Behavior:** Uses Google Places API to find real attractions based on user interests
```python
url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
# Maps interests to place types
interest_map = {
    "temple": ["hindu_temple", "church", "mosque", "place_of_worship"],
    "food": ["restaurant", "cafe", "food", "meal_takeaway"],
    "museum": ["museum", "art_gallery", "cultural_center"],
    ...
}
```

**Why it works:**
- Fetches **real attractions** from Google Places database for any city worldwide
- Maps user interests to appropriate Google place types
- Returns actual attraction names, addresses, ratings from Google Maps
- Includes real operating hours, admission info, and descriptions
- Smart interest matching (e.g., "temples" → searches hindu_temple, church, mosque)
- Falls back to mock data only if API fails
- Provides Google Maps links for each attraction

**Implementation Details:**
- API: Google Places Text Search
- Cost: Free tier ($200/month credit shared with Hotels/Trains)
- Interest categories: temple, food, museum, beach, shopping, nature, culture, technology, nightlife
- Returns: name, address, rating, hours, cost estimates, descriptions
- Link format: Google Maps URLs for navigation

**Supported Interests:**
- Religious sites (temples, churches, mosques)
- Food & dining (restaurants, cafes, markets)
- Culture (museums, art galleries, theaters)
- Nature (parks, beaches, hiking trails)
- Shopping (malls, markets, boutiques)
- Technology (tech centers, innovation hubs)
- Nightlife (bars, clubs, entertainment)

**Future Enhancements:**
- Add TripAdvisor integration for reviews and rankings
- Include real-time crowd levels
- Add ticket booking integration
- Include user-generated photos

---

### 8. `get_visa_requirements` (knowledge_tools.py) - **[MOVED TO DYNAMIC SECTION]**
**Current Behavior:** ✅ **NOW DYNAMIC** - Uses Passport Index API (free, no auth required)
```python
# Passport Index API - free, comprehensive
url = f"https://rough-sun-2523.fly.dev/visa/{nationality_code}/{destination_code}"
```

**Status:** ✅ **Fully Dynamic (Updated)**

**Why it works:**
- Uses free Passport Index API for real-time visa requirements
- Supports **ALL countries worldwide** (not just 4 hardcoded ones)
- Accepts user's nationality as input parameter for personalized requirements
- Returns actual visa categories: Visa Free, Visa on Arrival, eVisa, Visa Required
- Includes duration of stay from API data
- Falls back to static data only if API fails
- Uses RestCountries API to resolve country names to ISO codes

**Implementation:**
- Primary: Passport Index API (https://rough-sun-2523.fly.dev)
- Fallback: Static data for 4 countries (Japan, Italy, Thailand, France)
- Helper: RestCountries API for country code resolution
- No API key required
- No rate limits

**Future enhancements:**
- Add Sherpa° API for COVID/health requirements
- Include processing times, costs, required documents
- Add embassy location lookup

---

### 9. `get_currency_info` (knowledge_tools.py) - **[MOVED TO DYNAMIC SECTION]**
**Current Behavior:** ✅ **NOW DYNAMIC** - Uses RestCountries API + ExchangeRate-API (both free)
```python
# RestCountries API - free, comprehensive
url = f"https://restcountries.com/v3.1/name/{country}"
# ExchangeRate-API - free
rate_url = "https://api.exchangerate-api.com/v4/latest/USD"
```

**Status:** ✅ **Fully Dynamic (Updated)**

**Why it works:**
- Uses RestCountries API for currency data for **ALL countries worldwide**
- Real-time exchange rates from ExchangeRate-API
- Returns currency code, name, symbol, and current exchange rate to USD
- No hardcoded countries - works for any destination
- Falls back to static data only if APIs fail
- Completely free APIs with no authentication required

**Implementation:**
- Primary: RestCountries API (https://restcountries.com) for currency metadata
- Secondary: ExchangeRate-API (https://api.exchangerate-api.com) for live rates
- Fallback: Static data for 4 countries if both APIs fail
- No API key required
- No rate limits

**Returns:**
- Currency code (e.g., "JPY")
- Currency name (e.g., "Japanese yen")
- Symbol (e.g., "¥")
- Live exchange rate (e.g., "1 USD = 147.09 JPY")
- General usage notes

**Future enhancements:**
- Add historical rate trends
- Include ATM fee information by country
- Add currency conversion calculator
- Include best places to exchange money

---

### 10. `calculate_travel_time` (calculation_tools.py)
**Current Behavior:** Uses geopy for geodesic distance, assumes fixed 80 km/h average speed
```python
distance_km = geodesic(coords1, coords2).km
estimated_hours = distance_km / 80  # Fixed speed assumption
```

**Why it's partially dummy:**
- Uses real geocoding (good) but assumes fixed travel speed (bad)
- 80 km/h average is unrealistic for many scenarios (mountain roads, city traffic, air travel)
- Doesn't consider actual transport modes (train vs car vs plane)
- No consideration for terrain, infrastructure, or actual routes
- Fallback returns generic "3 hours, 200 km" for any failed calculation

**How to make dynamic:**
- Integrate with **Rome2Rio API** or **Google Directions API** for actual travel times by mode
- Use **Mapbox Directions API** or **HERE Maps API** as alternatives
- Calculate different times for different transport modes (train/car/bus/plane)
- Consider real road networks, not just straight-line distance
- Include real-time traffic data for car journeys
- For long distances, suggest flight options with actual flight times

**Suggested APIs:**
- Google Directions API: https://developers.google.com/maps/documentation/directions
- Rome2Rio API: Multi-modal with realistic times
- Mapbox Directions API: https://docs.mapbox.com/api/navigation/directions/

---

### 11. `local_transport_node` (city_processing.py) - **UPGRADED ✅**
**Status:** ✅ Fully dynamic (Recently implemented)
**Implementation:** Hybrid approach - Google Places API + Tavily Web Search

**Current Behavior:** Uses multiple data sources for comprehensive local transport info
```python
# Google Places for transit systems
transit_info = get_transit_system_info(city)  # e.g., "Tokyo Metro"

# Web search for specific details
day_pass_cost = search_transport_costs(city, country)
taxi_apps = search_taxi_apps(city, country)  # ["Uber", "Careem", "Grab"]
bike_rentals = search_bike_rentals(city, country)
```

**Why it works:**
- **Transit systems**: Google Places API finds real metro/subway station names
- **Day pass costs**: Web search extracts pricing from city transit websites
- **Taxi apps**: Web search identifies available ride-sharing services per city
- **Bike rentals**: Web search finds city-specific bike sharing services
- City-specific data (e.g., Dubai shows "Careem", Tokyo shows "Lime, Bird")
- Falls back to generic data only if all sources fail

**Implementation Details:**
- Transit API: Google Places Text Search (transit_station type)
- Search API: Tavily web search for costs, apps, bikes
- Cost: Free tier (shared with other Google/Tavily usage)
- Returns: metro_system, day_pass_cost, taxi_apps[], bike_rentals, walking_friendly, notes

**Example Output (Dubai vs Tokyo):**
- Dubai: metro_system="Dubai Metro", taxi_apps=["Uber", "Careem", "Hala"]
- Tokyo: metro_system="Tokyo Metro", taxi_apps=["Uber", "Lyft", "Grab"], bike_rentals="Lime, Bird"

**Recent Improvements:**
- ✅ Dynamic transit system names from Google Places
- ✅ City-specific taxi app detection via web search
- ✅ Bike sharing service identification
- ✅ Country parameter passed for better search context

---

### 12. `get_restaurant_recommendations` (city_processing.py) - **UPGRADED ✅**
**Status:** ✅ Fully dynamic (Recently implemented)
**Implementation:** Google Places API Text Search

**Current Behavior:** Finds real restaurants based on meal type and budget tier
```python
meal_queries = {
    "budget": {"breakfast": f"cheap breakfast cafe in {city}", ...},
    "moderate": {"breakfast": f"popular breakfast spot in {city}", ...},
    "luxury": {"breakfast": f"upscale breakfast brunch in {city}", ...}
}
```

**Why it works:**
- Fetches **real restaurants** from Google Places for each meal
- Budget-aware queries (cheap/popular/upscale)
- Meal-specific pricing ranges:
  - Breakfast: $5-25 depending on budget tier
  - Lunch: $10-40 depending on budget tier
  - Dinner: $15-80 depending on budget tier
- Returns restaurant name, cost estimate, and rating
- Called dynamically for each day of itinerary

**Implementation Details:**
- API: Google Places Text Search
- Meals covered: breakfast, lunch, dinner
- Budget tiers: budget, moderate, luxury
- Returns: name, cost, rating from Google
- Cost: Free tier (shared Google Places quota)

---

## SUMMARY TABLE

| Tool | Status | API Used | Priority |
|------|--------|----------|----------|
| `web_search` | ✅ Dynamic | Tavily API | N/A |
| `get_visa_requirements` | ✅ Dynamic **[UPGRADED]** | Passport Index API (free) | ✅ **DONE** |
| `get_currency_info` | ✅ Dynamic **[UPGRADED]** | RestCountries + ExchangeRate-API | ✅ **DONE** |
| `search_hotels` | ✅ Dynamic **[UPGRADED]** | Google Places API | ✅ **DONE** |
| `search_trains` | ✅ Dynamic **[UPGRADED]** | Google Directions API | ✅ **DONE** |
| `search_attractions` | ✅ Dynamic **[UPGRADED]** | Google Places API | ✅ **DONE** |
| `local_transport_node` | ✅ Dynamic **[UPGRADED]** | Google Places + Tavily Search | ✅ **DONE** |
| `get_restaurant_recommendations` | ✅ Dynamic **[UPGRADED]** | Google Places API | ✅ **DONE** |
| `optimize_route` | ⚠️ Mostly Dynamic | Nominatim (OSM) | Low |
| `calculate_travel_time` | ⚠️ Partially Static | Nominatim (OSM) | Low |

---

## RECOMMENDED IMPLEMENTATION ORDER

### ✅ Phase 0: Supporting Information (COMPLETED)
1. ✅ **get_currency_info** - Real-time currency data with exchange rates (RestCountries + ExchangeRate-API)
2. ✅ **get_visa_requirements** - Real visa requirements for all nationalities (Passport Index API)

### ✅ Phase 1: Critical Travel Data (COMPLETED)
1. ✅ **search_hotels** - Real hotel options with ratings ≥3.0, Google Maps links
2. ✅ **search_attractions** - Dynamic attractions based on user interests via Google Places
3. ✅ **search_trains** - Real transit routes via Google Directions with Rome2Rio/Omio booking links

### ✅ Phase 2: Enhanced Daily Planning (COMPLETED)
4. ✅ **get_restaurant_recommendations** - Real restaurants for breakfast/lunch/dinner per budget tier
5. ✅ **local_transport_node** - Dynamic transit info, taxi apps, bike rentals per city

### Phase 3: Optimization (Lower Priority) - **NEXT**
6. **calculate_travel_time** - Improve route planning accuracy with real transport data
7. **optimize_route** - Upgrade from greedy to optimal TSP solver

---

## COST CONSIDERATIONS

### ✅ Currently Using (All Free/Free Tier)
- ✅ **Tavily API** - Web search (free tier: 1,000 searches/month)
- ✅ **Google Places API** - Hotels, attractions, restaurants, transit ($200/month credit = ~900 trips)
- ✅ **Google Directions API** - Train routes ($200/month credit shared with Places)
- ✅ **RestCountries API** - Completely free, unlimited
- ✅ **ExchangeRate-API** - Free tier (1,500 requests/month)
- ✅ **Passport Index API** - Completely free, no auth required
- ✅ **Nominatim (OSM)** - Free but rate-limited (used for route optimization)

### Cost Breakdown (Monthly Estimates)
**Google Maps Platform** (Places + Directions):
- Free tier: $200/month credit
- Places Text Search: $17 per 1,000 requests
- Directions API: $5 per 1,000 requests
- Estimated usage per trip: ~15-20 API calls
- **Capacity: ~900 trips/month within free tier**

**Tavily Search API**:
- Free tier: 1,000 searches/month
- Usage: ~3-5 searches per trip (transport costs, taxi apps, bike rentals)
- **Capacity: ~200-300 trips/month within free tier**

**Other APIs**: All unlimited or sufficient free tiers

### Affiliate/Revenue Opportunities
- ✅ **Rome2Rio** - Affiliate links for train bookings (commission-based)
- ✅ **Omio** - Affiliate links for transport bookings (commission-based)
- 🔜 **Booking.com** - Future integration for hotel commissions
- 🔜 **TripAdvisor** - Future integration for attraction tickets

### Development Strategy
✅ **Phases 0-2 Complete**: All critical tools now dynamic using free tier APIs.
- Zero upfront cost
- ~200-900 trips/month capacity (limited by Tavily free tier)
- Revenue potential through affiliate links
**Next**: Monitor usage, upgrade APIs if traffic grows beyond free tiers.
