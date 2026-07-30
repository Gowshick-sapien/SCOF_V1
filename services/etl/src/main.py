import argparse
import logging
import sys
from services.etl.src.pipeline import ETLPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("scof-etl")

def main():
    parser = argparse.ArgumentParser(description="SCOF Deliverable D2 ETL Pipeline Service")
    parser.add_argument("--mode", choices=["full", "incremental"], default="full", help="Ingestion mode (full re-hydration or incremental update)")
    args = parser.parse_args()

    try:
        pipeline = ETLPipeline(mode=args.mode)
        stats = pipeline.run()
        print("\n--- D2 ETL Pipeline Execution Summary ---")
        for key, val in stats.items():
            print(f"  {key}: {val}")
        print("------------------------------------------\n")
    except Exception as e:
        logger.error("ETL Pipeline Execution Failed: %s", e, exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
