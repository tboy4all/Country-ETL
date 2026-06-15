import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.restcountries.com/countries/v5"


def fetch_countries():
    api_key = os.getenv("RESTCOUNTRIES_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing RESTCOUNTRIES_API_KEY in your .env file.\n"
            "Sign up free at https://restcountries.com/sign-up to get one."
        )

    headers = {"Authorization": f"Bearer {api_key}"}

    all_objects = []
    limit = 100  # max per page on v5
    offset = 0

    print("  Fetching all countries from REST Countries API v5...")

    while True:
        response = requests.get(
            BASE_URL,
            headers=headers,
            params={
                "limit": limit,
                "offset": offset,
                # Omit heavy/unused fields to keep responses lean
                "response_fields_omit": "names.translations,flag.description,links,leaders",
            },
            timeout=30,
        )
        response.raise_for_status()

        body = response.json()

        # V5 wraps everything under data.objects
        objects = body.get("data", {}).get("objects", [])
        meta = body.get("data", {}).get("meta", {})

        all_objects.extend(objects)

        print(f"  Fetched {len(all_objects)} / {meta.get('total', '?')} countries...")

        # Stop when there are no more pages
        if not meta.get("more", False):
            break

        offset += limit

    print(f"  ✅ Total fetched: {len(all_objects)} countries.")

    # Validate response shape
    if all_objects and not isinstance(all_objects[0], dict):
        raise ValueError(
            f"Unexpected API response format. "
            f"Expected list of dicts, got: {type(all_objects[0])}"
        )

    # Save raw data for debugging
    with open("raw_countries.json", "w", encoding="utf-8") as f:
        json.dump(all_objects, f, ensure_ascii=False, indent=2)

    print("  Raw data saved to raw_countries.json")
    return all_objects
