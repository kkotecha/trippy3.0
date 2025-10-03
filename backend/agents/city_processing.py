from graph.state import CityState, TripPlannerState
from tools import search_hotels, search_attractions
from langgraph.graph import StateGraph, END
import requests
import os

def get_restaurant_recommendations(city: str, meal_type: str, budget_tier: str) -> dict:
    """
    Get restaurant recommendations using Google Places API.

    Args:
        city: City name
        meal_type: "breakfast", "lunch", or "dinner"
        budget_tier: "budget", "moderate", or "luxury"

    Returns:
        Dict with restaurant name and estimated cost
    """
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    # Budget-based price ranges
    price_ranges = {
        "breakfast": {"budget": (5, 10), "moderate": (10, 15), "luxury": (15, 25)},
        "lunch": {"budget": (10, 15), "moderate": (15, 25), "luxury": (25, 40)},
        "dinner": {"budget": (15, 25), "moderate": (25, 40), "luxury": (40, 80)}
    }

    min_price, max_price = price_ranges[meal_type][budget_tier]
    mid_price = (min_price + max_price) // 2

    if google_api_key and google_api_key != "your_google_maps_api_key_here":
        try:
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

            # Query based on meal type and budget
            meal_queries = {
                "budget": {
                    "breakfast": f"cheap breakfast cafe in {city}",
                    "lunch": f"affordable local restaurant in {city}",
                    "dinner": f"budget-friendly dinner restaurant in {city}"
                },
                "moderate": {
                    "breakfast": f"popular breakfast spot in {city}",
                    "lunch": f"good restaurant for lunch in {city}",
                    "dinner": f"popular dinner restaurant in {city}"
                },
                "luxury": {
                    "breakfast": f"upscale breakfast brunch in {city}",
                    "lunch": f"fine dining lunch in {city}",
                    "dinner": f"fine dining restaurant in {city}"
                }
            }

            query = meal_queries[budget_tier][meal_type]

            params = {
                "query": query,
                "type": "restaurant",
                "key": google_api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "OK" and data.get("results"):
                # Get first result
                restaurant = data["results"][0]
                name = restaurant.get("name", f"Local {meal_type} spot")
                rating = restaurant.get("rating", "N/A")

                return {
                    "name": name,
                    "cost": f"${mid_price}",
                    "rating": rating
                }

        except Exception as e:
            print(f"Failed to get restaurant for {meal_type} in {city}: {e}")

    # Fallback to generic recommendations
    fallback_names = {
        "breakfast": "Local cafe",
        "lunch": "Restaurant near attractions",
        "dinner": "Traditional local cuisine"
    }

    return {
        "name": fallback_names[meal_type],
        "cost": f"${mid_price}",
        "rating": "N/A"
    }


def accommodation_node(state: CityState) -> dict:
    """Find accommodations for the city"""
    hotels = search_hotels.invoke({
        "city": state["city_name"],
        "nights": state["nights"],
        "budget_tier": state["budget_tier"]
    })
    return {"accommodation_options": hotels}

def itinerary_node(state: CityState) -> dict:
    """Create daily itinerary for the city"""
    city = state["city_name"]
    budget_tier = state["budget_tier"]

    attractions = search_attractions.invoke({
        "city": city,
        "interests": state["interests"],
        "max_results": state["nights"] * 3
    })

    # Create simple day-by-day plan
    daily_itinerary = []
    for day in range(1, state["nights"] + 1):
        start_idx = (day - 1) * 3
        day_attractions = attractions[start_idx:start_idx + 3]

        # Get dynamic meal recommendations for this day
        breakfast = get_restaurant_recommendations(city, "breakfast", budget_tier)
        lunch = get_restaurant_recommendations(city, "lunch", budget_tier)
        dinner = get_restaurant_recommendations(city, "dinner", budget_tier)

        # Calculate daily cost
        breakfast_cost = int(breakfast["cost"].replace("$", ""))
        lunch_cost = int(lunch["cost"].replace("$", ""))
        dinner_cost = int(dinner["cost"].replace("$", ""))

        # Add activity costs (estimate)
        activity_cost = sum([
            int(attr["cost"].replace("$", "").split("-")[0].split()[0])
            if "$" in str(attr["cost"]) else 20
            for attr in day_attractions
        ])

        daily_total = breakfast_cost + lunch_cost + dinner_cost + activity_cost

        daily_itinerary.append({
            "day": day,
            "title": f"Day {day} in {city}",
            "activities": [
                {
                    "time": "09:00" if i == 0 else "13:00" if i == 1 else "17:00",
                    "activity": attr["name"],
                    "location": attr["address"],
                    "duration": attr["duration_recommended"],
                    "cost": attr["cost"],
                    "tips": attr.get("description", "")
                }
                for i, attr in enumerate(day_attractions)
            ],
            "meals": {
                "breakfast": f"{breakfast['name']} ({breakfast['cost']})",
                "lunch": f"{lunch['name']} ({lunch['cost']})",
                "dinner": f"{dinner['name']} ({dinner['cost']})"
            },
            "daily_cost": f"${daily_total}"
        })

    return {"daily_itinerary": daily_itinerary}

def get_transit_system_info(city: str) -> dict:
    """Get transit system info using Google Places API"""
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if google_api_key and google_api_key != "your_google_maps_api_key_here":
        try:
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": f"metro subway station in {city}",
                "type": "transit_station",
                "key": google_api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "OK" and data.get("results"):
                # Get the most prominent transit station
                station = data["results"][0]
                name = station.get("name", f"{city} Metro")

                # Extract transit system name (usually in the name)
                # e.g., "Tokyo Metro Shibuya Station" -> "Tokyo Metro"
                system_name = name.split(" Station")[0].split(" -")[0]

                return {
                    "name": system_name,
                    "available": True
                }
        except Exception as e:
            print(f"Failed to get transit info for {city}: {e}")

    return {"name": f"{city} Public Transit", "available": False}


def search_transport_costs(city: str, country: str) -> str:
    """Search for day pass costs using web search"""
    try:
        from tools import web_search
        results = web_search.invoke(f"public transport day pass cost price in {city} {country} 2025")

        # Extract price info from results (simple parsing)
        if "$" in results or "USD" in results or "AED" in results or "€" in results:
            # Try to extract a reasonable estimate
            import re
            prices = re.findall(r'\$\d+(?:\.\d{2})?', results)
            if prices:
                return prices[0]

        return "$10 (estimated)"
    except Exception as e:
        print(f"Failed to search transport costs for {city}: {e}")
        return "$10 (estimated)"


def search_taxi_apps(city: str, country: str) -> list:
    """Search for taxi/ride-sharing apps using web search"""
    try:
        from tools import web_search
        results = web_search.invoke(f"taxi ride sharing apps available in {city} {country}")

        # Extract common app names
        common_apps = ["Uber", "Lyft", "Grab", "Gojek", "Careem", "Bolt", "Didi",
                      "Ola", "Cabify", "99", "Yandex", "Kakao", "Free Now", "Hala"]

        found_apps = []
        results_lower = results.lower()
        for app in common_apps:
            if app.lower() in results_lower:
                found_apps.append(app)

        # Return top 3 or default to Uber + local
        if found_apps:
            return found_apps[:3]

        return ["Uber", "Local taxis"]
    except Exception as e:
        print(f"Failed to search taxi apps for {city}: {e}")
        return ["Uber", "Local taxis"]


def search_bike_rentals(city: str, country: str) -> str:
    """Search for bike rental/sharing services using web search"""
    try:
        from tools import web_search
        results = web_search.invoke(f"bike rental sharing services in {city} {country}")

        # Extract common bike sharing names
        bike_services = ["Citi Bike", "Lime", "Bird", "Spin", "Jump", "Mobike",
                        "Ofo", "Santander", "Vélib", "Byky", "Careem Bike"]

        found_services = []
        results_lower = results.lower()
        for service in bike_services:
            if service.lower() in results_lower:
                found_services.append(service)

        if found_services:
            return ", ".join(found_services[:2])

        if "bike" in results_lower and "rental" in results_lower:
            return "Available (check locally)"

        return "Limited availability"
    except Exception as e:
        print(f"Failed to search bike rentals for {city}: {e}")
        return "Check locally"


def local_transport_node(state: CityState) -> dict:
    """Get local transportation info for the city - now dynamic!"""
    city = state["city_name"]
    country = state.get("country", "")  # Get country if available from state

    # Get transit system info from Google Places
    transit_info = get_transit_system_info(city)

    # Get costs, taxi apps, and bike info via web search
    day_pass_cost = search_transport_costs(city, country)
    taxi_apps = search_taxi_apps(city, country)
    bike_rentals = search_bike_rentals(city, country)

    transport_info = {
        "metro_system": transit_info["name"],
        "day_pass_cost": day_pass_cost,
        "taxi_apps": taxi_apps,
        "bike_rentals": bike_rentals,
        "walking_friendly": True,  # Could enhance with Google Walking Score
        "notes": f"Public transport {'available' if transit_info['available'] else 'may be limited'} in {city}"
    }

    return {"local_transport_info": transport_info}

def create_city_subgraph():
    """Create subgraph for processing one city"""
    city_graph = StateGraph(CityState)

    city_graph.add_node("accommodation", accommodation_node)
    city_graph.add_node("itinerary", itinerary_node)
    city_graph.add_node("local_transport", local_transport_node)

    city_graph.set_entry_point("accommodation")
    city_graph.add_edge("accommodation", "itinerary")
    city_graph.add_edge("itinerary", "local_transport")
    city_graph.add_edge("local_transport", END)

    return city_graph.compile()

def process_cities_node(state: TripPlannerState) -> dict:
    """Process all cities - calls nodes directly instead of using subgraph"""
    city_plans = []

    for city in state["city_route"]:
        city_state = {
            "city_name": city,
            "nights": state["nights_per_city"][city],
            "interests": state["interests"],
            "budget_tier": state["budget_tier"],
            "country": state["country"]  # Pass country for local transport
        }

        # Call nodes directly instead of invoking subgraph
        result = accommodation_node(city_state)
        city_state.update(result)

        result = itinerary_node(city_state)
        city_state.update(result)

        result = local_transport_node(city_state)
        city_state.update(result)

        city_plans.append({
            "city_name": city,
            "nights": city_state["nights"],
            "accommodation": city_state["accommodation_options"],
            "itinerary": city_state["daily_itinerary"],
            "local_transport": city_state["local_transport_info"]
        })

    return {"city_plans": city_plans}
