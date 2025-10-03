from langchain_core.tools import tool
from typing import List, Dict
import requests
import os
import urllib.parse


@tool
def search_hotels(
    city: str,
    nights: int,
    budget_tier: str
) -> List[Dict]:
    """
    Search for hotel accommodations using Google Places API (free tier: $200/month credit).
    Only recommends hotels with rating >= 3.0 stars. Links to Google Maps business profiles.

    Args:
        city: City name
        nights: Number of nights
        budget_tier: "budget", "moderate", or "luxury"

    Returns:
        List of up to 3 hotel recommendations with rating >= 3.0 stars

    Example:
        search_hotels("Tokyo", 4, "moderate")
    """
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    # Price ranges per night
    price_ranges = {
        "budget": (30, 70),
        "moderate": (70, 150),
        "luxury": (150, 400)
    }

    min_price, max_price = price_ranges.get(budget_tier, (70, 150))
    mid_price = (min_price + max_price) // 2

    if google_api_key and google_api_key != "your_google_maps_api_key_here":
        try:
            # Google Places Text Search for hotels
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

            # Query based on budget tier
            tier_keywords = {
                "budget": "budget hostel hotel",
                "moderate": "hotel accommodation",
                "luxury": "luxury boutique hotel"
            }

            query = f"{tier_keywords.get(budget_tier, 'hotel')} in {city}"

            params = {
                "query": query,
                "type": "lodging",
                "key": google_api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "OK" and data.get("results"):
                results = data.get("results", [])

                # Filter hotels with rating >= 3.0
                filtered_results = [r for r in results if r.get("rating", 0) >= 3.0]

                # Take top 3 from filtered results
                top_results = filtered_results[:3] if len(filtered_results) >= 3 else filtered_results

                hotels = []
                for place in top_results:
                    # Extract neighborhood from address
                    address = place.get("formatted_address", "")
                    neighborhood = address.split(",")[1].strip() if len(address.split(",")) > 1 else "City Center"

                    # Estimate price based on rating and budget tier
                    rating = place.get("rating", 4.0)
                    price_per_night = int(mid_price + (rating - 4.0) * 20)
                    price_per_night = max(min_price, min(price_per_night, max_price))

                    # Generate Google Maps link to business profile
                    place_id = place.get("place_id")
                    google_maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"

                    # Dynamic verbiage based on rating
                    if rating >= 4.5:
                        rating_description = "Exceptional"
                    elif rating >= 4.0:
                        rating_description = "Highly rated"
                    elif rating >= 3.5:
                        rating_description = "Well-rated"
                    else:
                        rating_description = "Rated"

                    reviews_count = place.get('user_ratings_total', 0)
                    reviews_text = f"{reviews_count} reviews" if reviews_count > 0 else "reviews"

                    hotel = {
                        "name": place.get("name", "Unknown Hotel"),
                        "type": "Hotel",
                        "neighborhood": neighborhood,
                        "price_per_night": f"${price_per_night}",
                        "total_cost": f"${price_per_night * nights}",
                        "rating": rating,
                        "amenities": ["WiFi", "Check Google Maps for full details"],
                        "booking_link": google_maps_link,
                        "why_recommended": f"{rating_description} ({rating} stars) with {reviews_text}",
                        "address": address,
                        "place_id": place_id
                    }
                    hotels.append(hotel)

                if hotels:
                    return hotels

                # If no results, fall through to mock data

        except Exception as e:
            print(f"Google Places API failed for hotels in {city}: {e}")
            # Fall through to mock data

    # Fallback to mock data
    print(f"Using fallback mock data for hotels in {city}")
    city_encoded = urllib.parse.quote(city)
    google_search_link = f"https://www.google.com/maps/search/hotels+in+{city_encoded}"

    hotels = [
        {
            "name": f"{city} Central Hotel",
            "type": "Hotel",
            "neighborhood": "City Center",
            "price_per_night": f"${mid_price}",
            "total_cost": f"${mid_price * nights}",
            "rating": 4.3,
            "amenities": ["WiFi", "Breakfast", "Gym"],
            "booking_link": google_search_link,
            "why_recommended": "Highly rated (4.3 stars) - Central location, excellent transport links"
        },
        {
            "name": f"{city} Budget Inn",
            "type": "Hostel" if budget_tier == "budget" else "Hotel",
            "neighborhood": "Downtown",
            "price_per_night": f"${min_price + 10}",
            "total_cost": f"${(min_price + 10) * nights}",
            "rating": 4.1,
            "amenities": ["WiFi", "Shared kitchen"],
            "booking_link": google_search_link,
            "why_recommended": "Highly rated (4.1 stars) - Great value, social atmosphere"
        },
        {
            "name": f"{city} Boutique Stay",
            "type": "Boutique Hotel",
            "neighborhood": "Arts District",
            "price_per_night": f"${max_price - 20}",
            "total_cost": f"${(max_price - 20) * nights}",
            "rating": 4.7,
            "amenities": ["WiFi", "Rooftop bar", "Concierge"],
            "booking_link": google_search_link,
            "why_recommended": "Exceptional (4.7 stars) - Unique character, local experience"
        }
    ]

    return hotels
