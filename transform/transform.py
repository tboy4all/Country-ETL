import pandas as pd


def get_first_item(value):
    """Safely return the first item from a list, or None."""
    if isinstance(value, list) and len(value) > 0:
        return value[0]
    return None


def transform(data):
    records = []

    for country in data:

        # ── Names ──────────────────────────────────────────────────────────
        names = country.get("names") or {}
        country_name = names.get("common")
        official_name = names.get("official")

        native_names = names.get("native") or {}
        if native_names:
            common_native = list(native_names.values())[0].get("common")
        else:
            common_native = None

        # ── Classification ─────────────────────────────────────────────────
        classification = country.get("classification") or {}
        independence = classification.get("sovereign")
        un_member = classification.get("un_member")

        # ── Start of week ──────────────────────────────────────────────────
        date_info = country.get("date") or {}
        start_of_week = date_info.get("start_of_week")

        # ── Calling code ───────────────────────────────────────────────────
        # V5: calling_codes is a plain list of strings e.g. ["+49"] or ["1"]
        calling_codes = country.get("calling_codes") or []
        if calling_codes:
            raw_code = str(calling_codes[0])
            # Ensure the + prefix is present
            country_code = raw_code if raw_code.startswith("+") else f"+{raw_code}"
        else:
            country_code = None

        # ── Currency ───────────────────────────────────────────────────────
        # V5: currencies is now a LIST of objects:
        # [{"code": "USD", "name": "US Dollar", "symbol": "$"}, ...]
        # (Previously it was a dict: {"USD": {"name": ..., "symbol": ...}})
        currencies = country.get("currencies") or []

        if isinstance(currencies, list) and currencies:
            first_currency = currencies[0]
            curr_code = first_currency.get("code")
            curr_name = first_currency.get("name")
            curr_symbol = first_currency.get("symbol")

        elif isinstance(currencies, dict) and currencies:
            # Fallback: handle old dict shape just in case
            curr_code = list(currencies.keys())[0]
            curr_name = currencies[curr_code].get("name")
            curr_symbol = currencies[curr_code].get("symbol")

        else:
            curr_code = curr_name = curr_symbol = None

        # ── Capital ────────────────────────────────────────────────────────
        # V5: capitals is a list of objects: [{"name": "Berlin", "primary": true, ...}]
        capitals_list = country.get("capitals") or []
        if capitals_list and isinstance(capitals_list[0], dict):
            capital = capitals_list[0].get("name")
        elif capitals_list and isinstance(capitals_list[0], str):
            capital = capitals_list[0]
        else:
            capital = None

        # ── Languages ──────────────────────────────────────────────────────
        # V5: languages is a list of objects:
        # [{"iso639_1": "de", "name": "German", "nativeName": "Deutsch"}, ...]
        languages_raw = country.get("languages") or []

        if languages_raw and isinstance(languages_raw[0], dict):
            language_names = [
                lang.get("name") for lang in languages_raw if lang.get("name")
            ]
        elif languages_raw and isinstance(languages_raw[0], str):
            # Fallback: plain list of strings
            language_names = languages_raw
        else:
            language_names = []

        languages = ", ".join(language_names) if language_names else None
        language_count = len(language_names)

        # ── Geography ──────────────────────────────────────────────────────
        region = country.get("region")
        subregion = country.get("subregion")

        # V5: area is an object: {"kilometers": 357114, "miles": 137988}
        area_obj = country.get("area") or {}
        if isinstance(area_obj, dict):
            area = area_obj.get("kilometers")
        elif isinstance(area_obj, (int, float)):
            # Fallback: plain number
            area = area_obj
        else:
            area = None

        population = country.get("population")

        continents_list = country.get("continents") or []
        continents = ", ".join(continents_list) if continents_list else None

        # ── Append ─────────────────────────────────────────────────────────
        records.append(
            {
                "country_name": country_name,
                "official_name": official_name,
                "common_native_name": common_native,
                "independence": independence,
                "un_member": un_member,
                "start_of_week": start_of_week,
                "currency_code": curr_code,
                "currency_name": curr_name,
                "currency_symbol": curr_symbol,
                "country_code": country_code,
                "capital": capital,
                "region": region,
                "subregion": subregion,
                "languages": languages,
                "language_count": language_count,
                "area": area,
                "population": population,
                "continents": continents,
            }
        )

    df = pd.DataFrame(records)

    # ── Data type cleanup ──────────────────────────────────────────────────
    df["area"] = pd.to_numeric(df["area"], errors="coerce")
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df["language_count"] = (
        pd.to_numeric(df["language_count"], errors="coerce").fillna(0).astype(int)
    )

    return df
