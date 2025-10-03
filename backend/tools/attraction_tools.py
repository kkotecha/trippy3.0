from langchain_core.tools import tool
from typing import List, Dict
import requests
import os


def _map_interest_to_place_type(interest: str) -> List[str]:
    """Map user interests to Google Places API types"""
    interest_map = {
        "temple": ["hindu_temple", "church", "mosque", "synagogue", "place_of_worship"],
        "temples": ["hindu_temple", "church", "mosque", "synagogue", "place_of_worship"],
        "food": ["restaurant", "cafe", "food", "meal_takeaway"],
        "museum": ["museum", "art_gallery"],
        "museums": ["museum", "art_gallery"],
        "art": ["art_gallery", "museum"],
        "technology": ["museum", "tourist_attraction"],
        "tech": ["museum", "tourist_attraction"],
        "shopping": ["shopping_mall", "store", "clothing_store"],
        "nature": ["park", "natural_feature"],
        "beach": ["natural_feature", "tourist_attraction"],
        "beaches": ["natural_feature", "tourist_attraction"],
        "nightlife": ["night_club", "bar"],
        "history": ["museum", "tourist_attraction"],
        "culture": ["museum", "tourist_attraction", "art_gallery"],
        "architecture": ["tourist_attraction", "place_of_worship"],
    }

    interest_lower = interest.lower()
    for key, types in interest_map.items():
        if key in interest_lower:
            return types

    # Default to general tourist attractions
    return ["tourist_attraction", "museum", "park"]


@tool
def search_attractions(
    city: str,
    interests: List[str],
    max_results: int = 10
) -> List[Dict]:
    """
    Find tourist attractions using Google Places API (free tier: $200/month credit).
    Falls back to mock data if API unavailable.

    Args:
        city: City name
        interests: List of interest categories
        max_results: Maximum attractions to return

    Returns:
        List of attractions with details

    Example:
        search_attractions("Tokyo", ["temples", "food"], 5)
    """
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if google_api_key and google_api_key != "your_google_maps_api_key_here":
        try:
            # Determine place types based on interests
            place_types = set()
            for interest in interests:
                place_types.update(_map_interest_to_place_type(interest))

            # Use Text Search for better results
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

            all_results = []

            # Search for each interest category
            for interest in interests[:3]:  # Limit to 3 interests to avoid too many API calls
                params = {
                    "query": f"{interest} attractions in {city}",
                    "key": google_api_key
                }

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data.get("status") == "OK":
                    all_results.extend(data.get("results", []))

            # Remove duplicates by place_id
            unique_places = {}
            for place in all_results:
                place_id = place.get("place_id")
                if place_id not in unique_places:
                    unique_places[place_id] = place

            # Format results
            attractions = []
            for place in list(unique_places.values())[:max_results]:
                attraction = {
                    "name": place.get("name", "Unknown"),
                    "rating": place.get("rating", "N/A"),
                    "address": place.get("formatted_address", "Address not available"),
                    "category": ", ".join(place.get("types", ["attraction"])[:2]),
                    "description": f"Popular {place.get('types', ['attraction'])[0].replace('_', ' ')}",
                    "hours": "Check Google Maps for current hours",
                    "cost": "Varies - check official website",
                    "duration_recommended": "2-3 hours",
                    "user_ratings_total": place.get("user_ratings_total", 0),
                    "place_id": place.get("place_id")
                }
                attractions.append(attraction)

            if attractions:
                return attractions

            # If no results, fall through to mock data

        except Exception as e:
            print(f"Google Places API failed for {city}: {e}")
            # Fall through to mock data

    # Fallback to mock data
    print(f"Using fallback mock data for attractions in {city}")
    all_attractions = [
        {
            "name": f"{city} Historic Temple",
            "category": "temple",
            "rating": 4.7,
            "cost": "Free (donations welcome)",
            "address": f"123 Temple St, {city}",
            "description": "Ancient temple with beautiful gardens",
            "hours": "6 AM - 6 PM",
            "duration_recommended": "1-2 hours",
            "user_ratings_total": 500
        },
        {
            "name": f"{city} Food Market",
            "category": "food",
            "rating": 4.8,
            "cost": "$10-30 for meals",
            "address": f"45 Market Ave, {city}",
            "description": "Local street food and fresh produce",
            "hours": "8 AM - 8 PM",
            "duration_recommended": "2-3 hours",
            "user_ratings_total": 800
        },
        {
            "name": f"{city} Art Museum",
            "category": "museum",
            "rating": 4.6,
            "cost": "$15",
            "address": f"78 Museum Rd, {city}",
            "description": "Contemporary and classical art collection",
            "hours": "10 AM - 6 PM, closed Mondays",
            "duration_recommended": "2-3 hours",
            "user_ratings_total": 350
        },
        {
            "name": f"{city} Technology Center",
            "category": "technology",
            "rating": 4.5,
            "cost": "$20",
            "address": f"90 Tech Plaza, {city}",
            "description": "Interactive tech exhibits and demos",
            "hours": "9 AM - 7 PM",
            "duration_recommended": "2-4 hours",
            "user_ratings_total": 200
        }
    ]

    # Filter by interests
    filtered = []
    for attraction in all_attractions:
        if any(interest.lower() in attraction['category'].lower()
               for interest in interests):
            filtered.append(attraction)

    # If no matches, return general attractions
    if not filtered:
        filtered = all_attractions

    return filtered[:max_results]
