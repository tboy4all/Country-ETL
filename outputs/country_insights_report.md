
# Country Data Insights Report

## Overview

The analysis was carried out on 254 country records extracted from the REST Countries API and loaded into PostgreSQL. The dataset includes country names, official names, native names, independence status, UN membership, currencies, calling codes, capitals, regions, subregions, languages, area, population, and continents.

## Key Findings

1. **French-speaking countries:** 46
2. **English-speaking countries:** 92
3. **Countries with more than one official language:** 100
4. **Countries using Euro as official currency:** 36
5. **Countries from Western Europe:** 8
6. **Countries that have not gained independence:** 53
7. **Distinct continents represented:** 7
8. **Countries whose week does not start on Monday:** 22
9. **Countries that are not UN members:** 61
10. **Countries that are UN members:** 193

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
