from langchain_core.tools import tool
import requests
from typing import Optional


def _get_country_code(country_name: str) -> Optional[str]:
    """
    Get ISO 3166-1 alpha-2 country code from country name using RestCountries API.
    Handles both country names and major city names.

    Args:
        country_name: Full country name (e.g., "Japan", "United States") or ISO code (e.g., "IN", "US")

    Returns:
        Two-letter country code (e.g., "JP", "US") or None if not found
    """
    # If already a 2-letter code, return as-is
    if len(country_name) == 2 and country_name.isalpha():
        return country_name.upper()

    # Map common cities to countries
    city_to_country = {
        "dubai": "AE",
        "abu dhabi": "AE",
        "tokyo": "JP",
        "kyoto": "JP",
        "osaka": "JP",
        "paris": "FR",
        "london": "GB",
        "new york": "US",
        "los angeles": "US",
        "singapore": "SG",
        "hong kong": "HK",
        "bangkok": "TH",
        "delhi": "IN",
        "mumbai": "IN",
        "sydney": "AU",
        "melbourne": "AU",
        "toronto": "CA",
        "vancouver": "CA",
        "rome": "IT",
        "milan": "IT",
        "barcelona": "ES",
        "madrid": "ES",
        "berlin": "DE",
        "amsterdam": "NL",
        "brussels": "BE",
        "zurich": "CH",
        "vienna": "AT",
        "prague": "CZ",
        "istanbul": "TR",
        "seoul": "KR",
        "beijing": "CN",
        "shanghai": "CN"
    }

    # Check if it's a known city
    country_name_lower = country_name.lower()
    if country_name_lower in city_to_country:
        return city_to_country[country_name_lower]

    try:
        url = f"https://restcountries.com/v3.1/name/{country_name}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()[0]
        return data.get("cca2")  # ISO 3166-1 alpha-2 code
    except Exception as e:
        print(f"Failed to get country code for {country_name}: {e}")
        return None


@tool
def get_visa_requirements(country: str, nationality: str = "US") -> str:
    """
    Get visa requirements using Passport Index API (free, no auth required).
    Falls back to static data if API unavailable.

    Args:
        country: Destination country name
        nationality: Passport holder's nationality (default: "US")

    Returns:
        Visa information string with requirements, stay duration, and notes

    Example:
        get_visa_requirements("Japan", "US")
    """
    try:
        # Get ISO country codes
        destination_code = _get_country_code(country)
        nationality_code = _get_country_code(nationality)

        if not destination_code or not nationality_code:
            raise ValueError("Could not resolve country codes")

        # Passport Index API - free, no key required
        url = f"https://rough-sun-2523.fly.dev/visa/{nationality_code}/{destination_code}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract visa information
        category = data.get("category", {})
        visa_type = category.get("name", "Unknown")
        visa_code = category.get("code", "")
        duration = data.get("dur")
        passport_country = data.get("passport", {}).get("name", nationality)
        dest_country = data.get("destination", {}).get("name", country)

        # Map visa types to user-friendly format
        visa_emoji = {
            "VF": "✅",  # Visa Free
            "VOA": "🎫",  # Visa on Arrival
            "EV": "💻",  # eVisa
            "VR": "🏛️",  # Visa Required
            "CR": "⚠️",  # COVID Restricted
            "NA": "❓"   # Not Available
        }

        emoji = visa_emoji.get(visa_code, "ℹ️")

        result = f"**Visa Requirements for {passport_country} citizens visiting {dest_country}:**\n\n"
        result += f"{emoji} Status: {visa_type}\n"

        if duration:
            result += f"Duration: {duration} days\n"

        result += f"\nNote: Always verify with the official {dest_country} embassy before travel."

        return result

    except Exception as e:
        print(f"Passport Index API failed for {country}: {e}")

        # Fallback to static information
        fallback_info = {
            "Japan": "✅ Visa-free for US/EU/Australian citizens for stays up to 90 days. Passport must be valid for duration of stay.",
            "Italy": "✅ Schengen visa. US/EU citizens visa-free for up to 90 days in 180-day period.",
            "Thailand": "✅ Visa-free for most nationalities for 30-60 days. Confirm based on your nationality.",
            "France": "✅ Schengen visa. US/EU citizens visa-free for up to 90 days in 180-day period.",
        }

        return fallback_info.get(
            country,
            f"Check visa requirements for {country} (nationality: {nationality}) at the embassy website or official government sources."
        )


@tool
def get_currency_info(country: str) -> dict:
    """
    Get real currency information for any country.
    Uses RestCountries API (free, no API key required).

    Args:
        country: Country name

    Returns:
        Currency code, name, symbol, exchange rate, and usage notes
    """
    try:
        # RestCountries API - free, comprehensive
        url = f"https://restcountries.com/v3.1/name/{country}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()[0]

        # Extract currency info
        currencies = data.get("currencies", {})
        if not currencies:
            raise ValueError("No currency data found")

        currency_code = list(currencies.keys())[0]
        currency_data = currencies[currency_code]

        # Get exchange rate from free API
        rate_url = "https://api.exchangerate-api.com/v4/latest/USD"
        rate_response = requests.get(rate_url, timeout=10)
        rate_response.raise_for_status()
        rates = rate_response.json()["rates"]

        exchange_rate = rates.get(currency_code, "N/A")

        return {
            "code": currency_code,
            "name": currency_data.get("name"),
            "symbol": currency_data.get("symbol", ""),
            "exchange_rate_to_usd": f"1 USD = {exchange_rate} {currency_code}" if exchange_rate != "N/A" else "N/A",
            "notes": "Widely accepted. ATMs available in major cities.",
            "country": data.get("name", {}).get("common", country)
        }
    except Exception as e:
        print(f"Currency info failed for {country}: {e}")
        return {
            "code": "Unknown",
            "symbol": "?",
            "notes": f"Check currency for {country} before travel"
        }
