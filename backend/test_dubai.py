import requests
import json

# Test Dubai trip to verify dynamic local transport
url = "http://localhost:8000/plan-trip"

payload = {
    "nationality": "India",
    "country": "Japan",
    "total_duration": 7,
    "interests": ["temples", "food", "culture"],
    "budget_tier": "moderate",
    "num_cities": 3,
    "starting_city": "Tokyo",
    "travel_pace": "moderate"
}

print("🌍 Submitting trip request for Japan...")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("-" * 60)

response = requests.post(url, json=payload)

if response.status_code == 200:
    result = response.json()

    # Extract local transport info
    if "city_plans" in result and len(result["city_plans"]) > 0:
        print("✅ Trip plan generated successfully!")

        for idx, city_plan in enumerate(result["city_plans"]):
            city_name = city_plan.get("city_name", f"City {idx+1}")
            local_transport = city_plan.get("local_transport", {})

            print(f"\n📍 Local Transport Info for {city_name}:")
            print(f"  Metro System: {local_transport.get('metro_system')}")
            print(f"  Day Pass Cost: {local_transport.get('day_pass_cost')}")
            print(f"  Taxi Apps: {', '.join(local_transport.get('taxi_apps', []))}")
            print(f"  Bike Rentals: {local_transport.get('bike_rentals')}")
            print(f"  Walking Friendly: {local_transport.get('walking_friendly')}")
            print(f"  Notes: {local_transport.get('notes')}")
            print("\n" + "=" * 60)
            print(f"Full local transport data for {city_name}:")
            print(json.dumps(local_transport, indent=2))
            print("=" * 60)
    else:
        print("⚠️ No city plans found in response")
        print(json.dumps(result, indent=2))
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
