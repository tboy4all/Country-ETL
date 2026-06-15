-- ============================================================
-- Countries ETL - Views for Metabase
-- Run ONCE after pipeline loads data:
--
--   sudo docker cp sql/views.sql countries_postgres:/tmp/views.sql
--   sudo docker exec -it countries_postgres psql -U admin -d countries_db -f /tmp/views.sql
--
-- These views appear in Metabase as ready-to-use tables.
-- ============================================================

-- Drop old views first so PostgreSQL can recreate them cleanly
DROP VIEW IF EXISTS vw_membership_summary CASCADE;
DROP VIEW IF EXISTS vw_area_ranking CASCADE;
DROP VIEW IF EXISTS vw_currency_summary CASCADE;
DROP VIEW IF EXISTS vw_continent_summary CASCADE;
DROP VIEW IF EXISTS vw_language_summary CASCADE;
DROP VIEW IF EXISTS vw_country_languages CASCADE;
DROP VIEW IF EXISTS vw_country_continents CASCADE;


-- ============================================================
-- View 1: Split countries by continent
-- Used for accurate continent counts and continent-based ranking
-- ============================================================

CREATE OR REPLACE VIEW vw_country_continents AS
SELECT
    c.country_name,
    c.official_name,
    c.region,
    c.subregion,
    c.population,
    c.area,
    c.un_member,
    c.independence,
    c.start_of_week,
    TRIM(x.continent) AS continent
FROM countries c
CROSS JOIN LATERAL unnest(
    string_to_array(COALESCE(c.continents, ''), ',')
) AS x(continent)
WHERE TRIM(x.continent) <> '';


-- ============================================================
-- View 2: Split countries by language
-- Used for accurate English/French language counts
-- ============================================================

CREATE OR REPLACE VIEW vw_country_languages AS
SELECT
    c.country_name,
    c.official_name,
    c.region,
    c.subregion,
    c.continents,
    c.population,
    TRIM(x.language) AS language
FROM countries c
CROSS JOIN LATERAL unnest(
    string_to_array(COALESCE(c.languages, ''), ',')
) AS x(language)
WHERE TRIM(x.language) <> '';


-- ============================================================
-- View 3: Language summary
-- Used for language KPIs and filters in Metabase
-- ============================================================

CREATE OR REPLACE VIEW vw_language_summary AS
SELECT
    c.country_name,
    c.official_name,
    c.continents,
    c.region,
    c.subregion,
    c.population,
    c.languages,
    c.language_count,

    CASE
        WHEN EXISTS (
            SELECT 1
            FROM vw_country_languages l
            WHERE l.country_name = c.country_name
            AND l.language ILIKE 'English'
        )
        THEN true
        ELSE false
    END AS speaks_english,

    CASE
        WHEN EXISTS (
            SELECT 1
            FROM vw_country_languages l
            WHERE l.country_name = c.country_name
            AND l.language ILIKE 'French'
        )
        THEN true
        ELSE false
    END AS speaks_french,

    CASE
        WHEN EXISTS (
            SELECT 1
            FROM vw_country_languages l
            WHERE l.country_name = c.country_name
            AND l.language ILIKE 'Arabic'
        )
        THEN true
        ELSE false
    END AS speaks_arabic,

    CASE
        WHEN EXISTS (
            SELECT 1
            FROM vw_country_languages l
            WHERE l.country_name = c.country_name
            AND l.language ILIKE 'Spanish'
        )
        THEN true
        ELSE false
    END AS speaks_spanish,

    CASE
        WHEN c.language_count > 1 THEN true
        ELSE false
    END AS is_multilingual

FROM countries c;


-- ============================================================
-- View 4: Continent summary
-- Used for continent count, continent population, and area visuals
-- ============================================================

CREATE OR REPLACE VIEW vw_continent_summary AS
SELECT
    continent,
    COUNT(DISTINCT country_name) AS total_countries,
    SUM(population) AS total_population,
    ROUND(AVG(population)::NUMERIC, 0) AS avg_population,
    ROUND(SUM(area)::NUMERIC, 2) AS total_area_km2,
    COUNT(DISTINCT country_name) FILTER (WHERE un_member IS TRUE) AS un_member_count,
    COUNT(DISTINCT country_name) FILTER (WHERE independence IS TRUE) AS independent_count
FROM vw_country_continents
GROUP BY continent
ORDER BY total_countries DESC;


-- ============================================================
-- View 5: Currency summary
-- Used for Euro count and currency distribution
-- ============================================================

CREATE OR REPLACE VIEW vw_currency_summary AS
SELECT
    currency_code,
    currency_name,
    currency_symbol,
    COUNT(*) AS country_count
FROM countries
WHERE currency_code IS NOT NULL
GROUP BY currency_code, currency_name, currency_symbol
ORDER BY country_count DESC;


-- ============================================================
-- View 6: Area and population ranking by continent
-- Used for top area and lowest population questions
-- ============================================================

CREATE OR REPLACE VIEW vw_area_ranking AS
SELECT
    country_name,
    continent,
    region,
    subregion,
    area,
    population,

    RANK() OVER (
        ORDER BY area DESC
    ) AS global_area_rank,

    RANK() OVER (
        PARTITION BY continent
        ORDER BY area DESC
    ) AS continent_area_rank,

    RANK() OVER (
        ORDER BY population DESC
    ) AS global_population_rank,

    RANK() OVER (
        PARTITION BY continent
        ORDER BY population ASC
    ) AS continent_low_population_rank

FROM vw_country_continents
WHERE area IS NOT NULL
AND area > 0;


-- ============================================================
-- View 7: Membership and independence summary
-- Used for UN member, independence, and start-of-week visuals
-- ============================================================

CREATE OR REPLACE VIEW vw_membership_summary AS
SELECT
    country_name,
    official_name,
    continents,
    region,
    subregion,
    un_member,
    independence,
    start_of_week,

    CASE
        WHEN un_member IS TRUE THEN 'UN Member'
        WHEN un_member IS FALSE THEN 'Not UN Member'
        ELSE 'Unknown'
    END AS un_status,

    CASE
        WHEN independence IS TRUE THEN 'Independent'
        WHEN independence IS FALSE THEN 'Not Independent'
        ELSE 'Unknown'
    END AS independence_status,

    CASE
        WHEN start_of_week IS NULL THEN 'Unknown'
        WHEN LOWER(start_of_week) = 'monday' THEN 'Monday'
        ELSE 'Non-Monday'
    END AS week_start_group

FROM countries;