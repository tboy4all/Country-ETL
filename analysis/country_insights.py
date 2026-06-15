import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

load_dotenv()

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def get_db_engine():
    db_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5433)),
        database=os.getenv("DB_NAME"),
    )

    return create_engine(db_url)


def split_values(value):
    """Convert comma-separated text into a clean list."""
    if pd.isna(value) or value == "":
        return []

    return [item.strip() for item in str(value).split(",") if item.strip()]


def has_language(language_list, language_name):
    """Check if a language exists in a country's language list."""
    return language_name.lower() in [lang.lower() for lang in language_list]


def print_section(title):
    print("\n" + title)
    print("-" * len(title))


def save_bar_chart(series, title, xlabel, ylabel, filename):
    plt.figure(figsize=(10, 6))
    series.plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename)
    plt.close()


def main():
    engine = get_db_engine()

    df = pd.read_sql("SELECT * FROM countries", engine)

    print("\nCOUNTRY DATA INSIGHTS")
    print("=" * 60)
    print(f"Total records analyzed: {len(df)}")

    # Prepare helper columns
    df["language_list"] = df["languages"].apply(split_values)
    df["continent_list"] = df["continents"].apply(split_values)

    if "language_count" not in df.columns:
        df["language_count"] = df["language_list"].apply(len)

    continent_df = df.explode("continent_list").rename(
        columns={"continent_list": "continent"}
    )

    continent_df = continent_df[
        continent_df["continent"].notna() & (continent_df["continent"] != "")
    ]

    # 1. Countries that speak French
    french_count = (
        df["language_list"].apply(lambda langs: has_language(langs, "French")).sum()
    )

    # 2. Countries that speak English
    english_count = (
        df["language_list"].apply(lambda langs: has_language(langs, "English")).sum()
    )

    # 3. Countries with more than one official language
    multiple_language_count = (df["language_count"] > 1).sum()

    # 4. Countries whose official currency is Euro
    euro_count = df["currency_code"].fillna("").str.upper().eq("EUR").sum()

    # 5. Countries from Western Europe
    western_europe_count = (
        df["subregion"]
        .fillna("")
        .str.lower()
        .isin(["western europe", "west europe"])
        .sum()
    )

    # 6. Countries that have not gained independence
    not_independent_count = df["independence"].eq(False).sum()

    # 7. Distinct continents and number of countries from each
    continent_counts = (
        continent_df.groupby("continent")["country_name"]
        .count()
        .sort_values(ascending=False)
    )

    distinct_continent_count = continent_counts.shape[0]

    # 8. Countries whose start of week is not Monday
    not_monday_count = (
        df["start_of_week"].notna()
        & df["start_of_week"].fillna("").str.lower().ne("monday")
    ).sum()

    # 9. Countries that are not UN members
    not_un_member_count = df["un_member"].eq(False).sum()

    # 10. Countries that are UN members
    un_member_count = df["un_member"].eq(True).sum()

    print_section("Summary Questions")
    print(f"1. Countries that speak French: {french_count}")
    print(f"2. Countries that speak English: {english_count}")
    print(f"3. Countries with more than 1 official language: {multiple_language_count}")
    print(f"4. Countries whose official currency is Euro: {euro_count}")
    print(f"5. Countries from Western Europe: {western_europe_count}")
    print(f"6. Countries that have not gained independence: {not_independent_count}")
    print(f"7. Distinct continents: {distinct_continent_count}")
    print(f"8. Countries whose start of week is not Monday: {not_monday_count}")
    print(f"9. Countries that are not UN members: {not_un_member_count}")
    print(f"10. Countries that are UN members: {un_member_count}")

    print_section("Countries per Continent")
    print(continent_counts.to_string())

    # 11. Least 2 countries with lowest population for each continent
    lowest_population_by_continent = (
        # continent_df.dropna(subset=["continent", "population"])
        continent_df.dropna(subset=["continent", "population"])
        .query("population > 0")
        .sort_values(["continent", "population"], ascending=[True, True])
        .groupby("continent")
        .head(2)[["continent", "country_name", "population"]]
    )

    print_section("Least 2 Countries with Lowest Population per Continent")
    print(lowest_population_by_continent.to_string(index=False))

    # 12. Top 2 countries with largest area for each continent
    largest_area_by_continent = (
        continent_df.dropna(subset=["continent", "area"])
        .query("area > 0")
        .sort_values(["continent", "area"], ascending=[True, False])
        .groupby("continent")
        .head(2)[["continent", "country_name", "area"]]
    )

    print_section("Top 2 Countries with Largest Area per Continent")
    print(largest_area_by_continent.to_string(index=False))

    # 13. Top 5 countries with largest area
    top_5_largest_area = (
        df.dropna(subset=["area"])
        .query("area > 0")
        .sort_values("area", ascending=False)
        .head(5)[["country_name", "region", "subregion", "area"]]
    )

    print_section("Top 5 Countries with Largest Area")
    print(top_5_largest_area.to_string(index=False))

    # 14. Top 5 countries with lowest area
    top_5_lowest_area = (
        df.dropna(subset=["area"])
        .query("area > 0")
        .sort_values("area", ascending=True)
        .head(5)[["country_name", "region", "subregion", "area"]]
    )

    print_section("Top 5 Countries with Lowest Area")
    print(top_5_lowest_area.to_string(index=False))

    # Save CSV outputs
    continent_counts.to_csv(OUTPUT_DIR / "continent_counts.csv")
    lowest_population_by_continent.to_csv(
        OUTPUT_DIR / "lowest_population_by_continent.csv", index=False
    )
    largest_area_by_continent.to_csv(
        OUTPUT_DIR / "largest_area_by_continent.csv", index=False
    )
    top_5_largest_area.to_csv(OUTPUT_DIR / "top_5_largest_area.csv", index=False)
    top_5_lowest_area.to_csv(OUTPUT_DIR / "top_5_lowest_area.csv", index=False)

    # Save visualization files
    save_bar_chart(
        continent_counts,
        "Number of Countries per Continent",
        "Continent",
        "Number of Countries",
        "countries_per_continent.png",
    )

    save_bar_chart(
        top_5_largest_area.set_index("country_name")["area"],
        "Top 5 Countries with Largest Area",
        "Country",
        "Area",
        "top_5_largest_area.png",
    )

    save_bar_chart(
        top_5_lowest_area.set_index("country_name")["area"],
        "Top 5 Countries with Lowest Area",
        "Country",
        "Area",
        "top_5_lowest_area.png",
    )

    # Creative insight report
    report = f"""
# Country Data Insights Report

## Overview

The analysis was carried out on {len(df)} country records extracted from the REST Countries API and loaded into PostgreSQL. The dataset includes country names, official names, native names, independence status, UN membership, currencies, calling codes, capitals, regions, subregions, languages, area, population, and continents.

## Key Findings

1. **French-speaking countries:** {french_count}
2. **English-speaking countries:** {english_count}
3. **Countries with more than one official language:** {multiple_language_count}
4. **Countries using Euro as official currency:** {euro_count}
5. **Countries from Western Europe:** {western_europe_count}
6. **Countries that have not gained independence:** {not_independent_count}
7. **Distinct continents represented:** {distinct_continent_count}
8. **Countries whose week does not start on Monday:** {not_monday_count}
9. **Countries that are not UN members:** {not_un_member_count}
10. **Countries that are UN members:** {un_member_count}

## Insight Interpretation

The language results show how global influence is reflected in official languages. English and French appear across many countries, which suggests their continued importance in administration, education, diplomacy, and international communication.

The number of countries with more than one official language also shows that many countries are multilingual by law or governance structure. This is important for public service delivery, education planning, and digital product localization.

The Euro currency count gives insight into economic integration, especially in Europe. Countries using the Euro are often linked through shared monetary policy and regional economic cooperation.

The independence and UN membership analysis separates fully sovereign states from territories, dependencies, and special administrative areas. This is important because not every record in a country dataset represents an independent nation-state.

The continent distribution shows how the dataset is spread geographically. It also helps reveal whether the data contains mostly sovereign countries or includes smaller territories and island regions.

The area and population rankings show that land size and population size do not always move together. Some countries have very large land areas but low population density, while some small countries or territories have very small populations and land sizes.

## Generated Files

- continent_counts.csv
- lowest_population_by_continent.csv
- largest_area_by_continent.csv
- top_5_largest_area.csv
- top_5_lowest_area.csv
- countries_per_continent.png
- top_5_largest_area.png
- top_5_lowest_area.png
"""

    with open(OUTPUT_DIR / "country_insights_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print_section("Output Files Created")
    print(f"Files saved inside: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
