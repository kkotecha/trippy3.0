from langchain_core.tools import tool
from typing import Dict
import requests
import os
import urllib.parse


@tool
def search_trains(
    from_city: str,
    to_city: str,
    country: str
) -> Dict:
    """
    Search for train/transit routes using Google Directions API (transit mode).
    Falls back to mock data if API unavailable. Generates booking links to Rome2Rio/Omio.

    Args:
        from_city: Departure city
        to_city: Arrival city
        country: Country name

    Returns:
        Train options with method, duration, cost, booking info

    Example:
        search_trains("Tokyo", "Kyoto", "Japan")
    """
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if google_api_key and google_api_key != "your_google_maps_api_key_here":
        try:
            # Google Directions API with transit mode
            url = "https://maps.googleapis.com/maps/api/directions/json"

            params = {
                "origin": from_city,
                "destination": to_city,
                "mode": "transit",
                "transit_mode": "train|rail",
                "key": google_api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "OK" and data.get("routes"):
                route = data["routes"][0]
                leg = route["legs"][0]

                # Extract transit details
                duration = leg.get("duration", {}).get("text", "Unknown duration")
                distance = leg.get("distance", {}).get("text", "Unknown distance")

                # Try to find train/rail steps
                train_steps = []
                for step in leg.get("steps", []):
                    if step.get("travel_mode") == "TRANSIT":
                        transit_details = step.get("transit_details", {})
                        line = transit_details.get("line", {})
                        vehicle_type = line.get("vehicle", {}).get("type", "TRAIN")

                        if "RAIL" in vehicle_type or "TRAIN" in vehicle_type:
                            train_steps.append({
                                "line": line.get("name", "Train"),
                                "vehicle": line.get("vehicle", {}).get("name", "Train"),
                                "duration": step.get("duration", {}).get("text", "")
                            })

                # Estimate cost based on distance (rough approximation)
                distance_km = leg.get("distance", {}).get("value", 100000) / 1000
                estimated_cost = int(distance_km * 0.15)  # Rough estimate: $0.15/km

                # Generate booking links
                from_encoded = urllib.parse.quote(f"{from_city}, {country}")
                to_encoded = urllib.parse.quote(f"{to_city}, {country}")
                rome2rio_link = f"https://www.rome2rio.com/map/{from_encoded}/{to_encoded}"
                omio_link = f"https://www.omio.com/search/{from_encoded}/{to_encoded}"

                # Format transit method
                if train_steps:
                    method = train_steps[0]["line"]
                else:
                    method = "Train/Rail transit"

                return {
                    "method": method,
                    "duration": duration,
                    "distance": distance,
                    "cost": f"${estimated_cost} (estimated)",
                    "booking_info": f"Book via Rome2Rio or Omio",
                    "booking_links": {
                        "rome2rio": rome2rio_link,
                        "omio": omio_link
                    },
                    "frequency": "Check schedule on booking site",
                    "notes": f"Route includes {len(train_steps)} train segment(s)" if train_steps else "Transit available"
                }

            # If no transit route found, fall through to mock data

        except Exception as e:
            print(f"Google Directions API failed for {from_city} to {to_city}: {e}")
            # Fall through to mock data

    # Fallback to mock data
    print(f"Using fallback mock data for train from {from_city} to {to_city}")

    # Mock database for known routes
    routes = {
        ("Tokyo", "Kyoto", "Japan"): {
            "method": "Shinkansen (bullet train)",
            "duration": "2h 15min",
            "cost": "$130",
            "booking_info": "Book via JR Pass or at station",
            "frequency": "Every 10-20 minutes",
            "notes": "Covered by JR Pass"
        },
        ("Kyoto", "Osaka", "Japan"): {
            "method": "JR Special Rapid",
            "duration": "30 minutes",
            "cost": "$8",
            "booking_info": "No reservation needed",
            "frequency": "Every 10 minutes",
            "notes": "Very frequent service"
        },
        ("Paris", "Lyon", "France"): {
            "method": "TGV",
            "duration": "2 hours",
            "cost": "$70",
            "booking_info": "Book via SNCF or Trainline",
            "frequency": "Hourly",
            "notes": "Book early for discounts"
        }
    }

    key = (from_city, to_city, country)
    if key in routes:
        return routes[key]

    # Generic fallback with booking links
    from_encoded = urllib.parse.quote(f"{from_city}, {country}")
    to_encoded = urllib.parse.quote(f"{to_city}, {country}")

    return {
        "method": "Train (check local schedules)",
        "duration": "3-5 hours",
        "cost": "$50-100 (estimated)",
        "booking_info": f"Check {country} national railway or Rome2Rio",
        "booking_links": {
            "rome2rio": f"https://www.rome2rio.com/map/{from_encoded}/{to_encoded}",
            "omio": f"https://www.omio.com/search/{from_encoded}/{to_encoded}"
        },
        "frequency": "Varies",
        "notes": "Exact schedules available on booking sites"
    }
