# Dagster pipeline definition
from dagster import job, op, repository, ScheduleDefinition
import os
from dotenv import load_dotenv

load_dotenv()

@op
def scrape_telegram_data():
    # Assuming scraper is in src/scraper/
    from src.scraper.telegram_scraper import main
    main()

@op
def load_raw_to_postgres():
    from src.dbt_project.load_raw_data import load_json_files
    load_json_files()

@op
def run_dbt_transformations():
    os.system("cd src/dbt_project && dbt run --profiles-dir .")

@op
def run_yolo_enrichment():
    from src.scraper.yolo.process_images import process_new_images
    process_new_images()

@op
def deploy_fastapi():
    # In production, this would deploy the API
    print("API would be deployed here")

@job
def medical_data_pipeline():
    raw_data = scrape_telegram_data()
    loaded = load_raw_to_postgres(raw_data)
    transformed = run_dbt_transformations(loaded)
    enriched = run_yolo_enrichment(transformed)
    deploy_fastapi(enriched)

daily_schedule = ScheduleDefinition(
    job=medical_data_pipeline,
    cron_schedule="0 2 * * *"  # Run daily at 2 AM UTC
)

@repository
def medical_data_repo():
    return [medical_data_pipeline, daily_schedule]