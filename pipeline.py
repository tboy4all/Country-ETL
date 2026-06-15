from extract.fetch_countries import fetch_countries
from transform.transform import transform
from load.load_to_db import load


def run_pipeline():
    print("=" * 50)
    print("  Countries ETL Pipeline Starting")
    print("=" * 50)

    try:
        # ── Step 1: Extract ───────────────────────────────
        print("\n[Step 1/3] Extracting data from REST Countries API...")
        data = fetch_countries()
        print(f"  Extract complete: {len(data)} countries retrieved.\n")

        # ── Step 2: Transform ─────────────────────────────
        print("[Step 2/3] Transforming data...")
        df = transform(data)
        print(f"  Transform complete: {len(df)} rows, {len(df.columns)} columns.")
        print(f"  Columns: {list(df.columns)}\n")

        # ── Step 3: Load ──────────────────────────────────
        print("[Step 3/3] Loading data into PostgreSQL...")
        load(df)

        print("\n" + "=" * 50)
        print("  ✅ Pipeline completed successfully!")
        print("=" * 50)

    except requests.exceptions.ConnectionError:
        print("\n❌ Network error: Could not reach the REST Countries API.")
        print("   Check your internet connection and try again.")
        raise

    except Exception as e:
        print(f"\n❌ Pipeline failed at an unexpected step: {e}")
        raise


if __name__ == "__main__":
    import requests  # noqa: imported here only for the except clause above

    run_pipeline()
