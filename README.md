# Dark Pool Liquidity Dashboard

## Overview

The **Dark Pool Liquidity Dashboard** is a real-time data pipeline and interactive visualization tool that exposes hidden liquidity in financial markets. By ingesting, processing, and visualizing high-volume trade data from dark pools and alternative trading systems (ATS), the dashboard delivers actionable insights into market microstructure and liquidity fragmentation.

## Features

- **Real-Time Data Pipeline:** Simulates streaming trade data using Kafka.
- **Stream Processing:** Python-based aggregator computes 5-minute rolling analytics (trade value, quantity, count) by symbol and venue.
- **REST API:** Flask server provides low-latency access to aggregated data.
- **Interactive Dashboard:** Single-page web app (HTML, Tailwind CSS, Chart.js) for dynamic exploration of liquidity trends.
- **Geospatial Visualization:** KeplerGL integration for mapping liquidity hotspots.
- **Offline Analytics:** Python scripts for advanced analysis and BI integration.

## Architecture

- **Data Generation:** Synthetic trades ingested via `data_producer.py`.
- **Messaging Backbone:** Apache Kafka decouples data ingestion, processing, and serving.
- **Stream Aggregation:** `simple_aggregator.py` performs real-time windowed analytics.
- **API Layer:** `api_server.py` exposes aggregated data through REST endpoints.
- **Visualization:** Dashboard and KeplerGL consume API data for interactive exploration.

## Technology Stack

- **Kafka:** High-throughput, fault-tolerant message broker.
- **Python:** Data ingestion, aggregation, and API serving.
- **Flask:** Lightweight, scalable REST API.
- **HTML/Tailwind CSS/Chart.js:** Responsive, interactive dashboard.
- **KeplerGL:** Browser-based geospatial analytics.
- **Pandas/Matplotlib/Seaborn:** Offline data analysis and reporting.

## Quick Start

### Prerequisites

- Python 3.9+ (recommended)
- Apache Kafka & ZooKeeper
- Git

### Setup

```bash
git clone https://github.com/RishiRCarnoli/dark-pool-project.git
cd dark-pool-project

# Set up Python environment
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Ensure `synthetic_darkpool_heavy.csv` is in the project root.

### Running Components (use separate terminals)

1. **ZooKeeper:**  
   `zookeeper-server-start /path/to/zookeeper.properties`
2. **Kafka Broker:**  
   `kafka-server-start /path/to/server.properties`
3. **Data Producer:**  
   `python data_producer.py`
4. **Aggregator:**  
   `python simple_aggregator.py`
5. **API Server:**  
   `python api_server.py`

Access the dashboard at [http://localhost:5001](http://localhost:5001).
