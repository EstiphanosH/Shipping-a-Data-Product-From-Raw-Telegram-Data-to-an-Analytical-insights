
# 🚢 Shipping a Data Product: From Raw Telegram Data to Analytical Insights

An end-to-end data platform to extract, transform, enrich, and serve Telegram data for strategic medical insights in Ethiopia.

---

## 📌 Project Summary

This project builds a robust, containerized data pipeline that ingests public Telegram data from Ethiopian medical channels, cleans and structures it using dbt, enriches it with object detection via YOLOv8, and serves business insights through an analytical API powered by FastAPI. The entire workflow is orchestrated with Dagster for reliability and automation.

---

## 🛠️ Tech Stack (Detailed)

| Layer | Technology | Purpose |
|------|------------|---------|
| **Infrastructure** | Docker, Docker Compose | Containerization of Python services, PostgreSQL, and orchestration environments |
| **Environment Management** | python-dotenv, .env files | Secure handling of secrets and environment configurations |
| **Data Ingestion** | Telethon | Scraping public Telegram messages and images |
| **Data Lake** | JSON Files in `/data/raw/` | Storing raw scraped data in partitioned structure |
| **Data Warehouse** | PostgreSQL | Centralized structured storage for dbt to operate |
| **Data Transformation** | dbt (dbt-core, dbt-postgres) | Building reliable, tested star schema models |
| **Image Enrichment** | YOLOv8 (Ultralytics), OpenCV, Torch | Detecting and classifying objects from Telegram image content |
| **API Layer** | FastAPI, Uvicorn, Pydantic | Serving analytics via well-structured RESTful endpoints |
| **Pipeline Orchestration** | Dagster, dagster-webserver | Managing and scheduling end-to-end workflows |
| **Testing** | pytest, dbt tests | Validating models, endpoints, and integration steps |

---

## 📁 Directory Structure

```
Shipping-a-Data-Product-From-Raw-Telegram-Data-to-an-Analytical-insights/
├── data/
│   ├── raw/telegrammessages/YYYY-MM-DD/channelname.json
│   └── processed/
├── docs/
│   ├── pipeline_diagram.png
│   └── star_schema_diagram.png
├── src/
│   ├── scraper/                 # Telegram scraping scripts
│   ├── dbt_project/            # DBT models and configurations
│   ├── yolo/                   # YOLO object detection scripts
│   ├── api/                    # FastAPI application
│   └── dagster/                # Dagster jobs and schedules
├── docker/                     # Docker & Compose setup
├── .env.example                # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

```bash
# Clone the repo
git clone https://github.com/yourusername/shipping-data-product.git
cd shipping-data-product

```

# Setup environment
cp .env.example .env

```

# Start infrastructure
docker-compose -f docker/docker-compose.yml up --build -d
```

---

## 🔍 Features by Task

### 📥 Task 1: Telegram Data Scraping
- Scrapes text and media from public health-related Telegram channels.
- Organizes raw data into timestamped JSON structure.
- Logs scraping process and handles rate limits.

### 🏗️ Task 2: Data Modeling with dbt
- Loads raw data into PostgreSQL (`raw` schema).
- Transforms data via staging models → marts (`dim_channels`, `dim_dates`, `fct_messages`).
- Includes tests, documentation, and lineage tracking.

### 🧠 Task 3: Enrichment with YOLOv8
- Detects medical objects (e.g., pills, syringes) in Telegram images.
- Stores detection results in `fct_image_detections` linked to messages.

### 🌐 Task 4: Analytical API with FastAPI
- `/api/reports/top-products` — most mentioned products.
- `/api/channels/{channel_name}/activity` — daily/weekly activity.
- `/api/search/messages` — full-text message search.

### 🧩 Task 5: Orchestration with Dagster
- End-to-end pipeline definition as reusable `ops`.
- Includes scheduling, logging, and a web UI for management.

---

## ✅ Testing

- Run dbt model tests: `dbt test`
- API unit tests: `pytest`
- Validate orchestration flow via `dagster dev` UI

---

## 📜 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- [10 Academy](https://10academy.org/)
- [Ultralytics YOLOv8](https://docs.ultralytics.com/)
- [DBT Documentation](https://docs.getdbt.com/)
- [Dagster](https://dagster.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Telethon](https://docs.telethon.dev/en/stable/)

