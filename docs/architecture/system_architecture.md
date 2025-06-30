# System Architecture-- AI-Powered Stock Trend Prediction Platform (Revised)

## 1. High-Level Architecture

This document outlines the revised high-level architecture for the AI-Powered Stock Trend Prediction Platform. The system is designed as a modular, service-oriented architecture, enhanced with robust orchestration, explicit state management, and a continuous feedback loop to ensure scalability, resilience, and long-term model efficacy.

The following diagram illustrates the primary modules, their interactions, and the flow of data. It now includes a **Model Registry** and a **Monitoring & Retraining Loop**.

```mermaid
graph TD
    subgraph User Facing
        Frontend_UI(Frontend UI - React)
    end

    subgraph Backend Services
        Backend_API(Backend API - FastAPI)
        Orchestrator(Pipeline Orchestrator -- Airflow/Dagster)
    end

    subgraph Data & Model Plane
        Database[(Database - PostgreSQL)]
        Cache[(Cache - Redis)]
        DataStore([Data Store - S3])
        ModelRegistry([Model Registry - MLflow])
    end

    subgraph Daily Prediction Pipeline
        A[IngestionJob]
        B[ProcessingJob]
        D[PredictionJob]
    end
    
    subgraph Monitoring & Retraining Loop
        E[PerformanceMonitoringJob]
        F[RetrainingJob]
    end

    subgraph Data Sources
        AlphaVantage([Alpha Vantage API])
        Twitter([Twitter API])
    end

    -- User Interaction --
    Frontend_UI -- API Requests -- Backend_API
    Backend_API -- Predictions & Watchlist Data -- Frontend_UI
    Backend_API -- Read/Write -- Database
    Backend_API -- Read/Write -- Cache

    -- Orchestrated Prediction Workflow --
    Orchestrator -- Manages State & Triggers -- A
    Orchestrator -- Manages State & Triggers -- B
    Orchestrator -- Manages State & Triggers -- D
    
    A -- Fetches -- AlphaVantage
    A -- Fetches -- Twitter
    A -- Writes Raw Data -- DataStore
    B -- Reads Raw Data -- DataStore
    B -- Writes Processed Features -- DataStore
    D -- Reads Processed Features -- DataStore
    D -- Writes Predictions -- Database

    -- Model Lifecycle --
    B -- Loads Model -- ModelRegistry
    D -- Loads Model -- ModelRegistry
    F -- Registers New Model -- ModelRegistry
    
    -- Feedback Loop --
    Orchestrator -- Schedules -- E
    E -- Reads Predictions & Actuals -- Database
    E -- Triggers Alert/Retraining -- Orchestrator
    Orchestrator -- Triggers -- F
    F -- Reads All Data -- DataStore

    style Frontend_UI fill:#f9f,stroke:#333,stroke-width:2px
    style Backend_API fill:#ccf,stroke:#333,stroke-width:2px
    style Orchestrator fill:#cce,stroke:#333,stroke-width:4px
    style Database fill:#f99,stroke:#333,stroke-width:2px
    style Cache fill:#f99,stroke:#333,stroke-width:2px
    style DataStore fill:#f99,stroke:#333,stroke-width:2px
    style ModelRegistry fill:#9cf,stroke:#333,stroke-width:4px
```

## 2. Module Breakdown

### 2.1. Data Ingestion Module

-   **Responsibility--** Fetches raw data from external sources. It handles API interactions, authentication, and rate limiting. It is responsible for placing the raw, unchanged data into the central `Data Store`.
-   **Components--**
    -   `AlphaVantageClient`-- Fetches historical daily stock prices.
    -   `TwitterClient`-- Fetches recent tweets related to specific stock tickers.
-   **Output--** Raw data files (e.g., JSON or Parquet) stored in a versioned location within the `Data Store` (e.g., `s3://bucket/raw-data/YYYY-MM-DD/`).

### 2.2. Data Processing Module

-   **Responsibility--** Transforms raw data from the `Data Store` into a feature-rich dataset suitable for the prediction model.
-   **Components--**
    -   `TweetProcessor`-- Cleans and tokenizes raw tweet text.
    -   `FeatureEngineer`-- Calculates technical indicators (Moving Averages, RSI, MACD, etc.).
    -   `SentimentAnalysisModel`-- Loads the production sentiment model from the **Model Registry** to generate sentiment scores.
-   **Output--** Feature-engineered datasets stored in the `Data Store` (e.g., `s3://bucket/processed-data/YYYY-MM-DD/`).

### 2.3. Prediction Model Module

-   **Responsibility--** Generates future stock price trend predictions.
-   **Components--**
    -   `PredictionModel`-- Encapsulates the LSTM model lifecycle. The prediction component loads the production-tagged model from the **Model Registry** to make predictions.
-   **Output--** Predictions (signal and confidence) written to the `Database`.

### 2.4. Backend API Module

-   **Responsibility--** Exposes the system's functionality to the frontend client via a RESTful API. It handles user requests, interacts with the database and cache, and serves prediction data.
-   **Components--**
    -   **API Endpoints**-- REST endpoints for searching stocks, getting predictions, and managing watchlists.
    -   `PredictionCache`-- A caching layer (Redis) to store recent prediction results.

### 2.5. Pipeline Orchestrator

-   **Responsibility--** Manages the entire execution, state, and dependency of all data and ML jobs. This component is the brain of the pipeline, ensuring resilience and visibility.
-   **Technology--** A data-aware orchestrator like **Apache Airflow** or **Dagster** is required. These tools provide critical features out-of-the-box that a generic task queue like Celery lacks, such as DAG visualization, state management, complex dependency handling, and operational monitoring.
-   **State Management--** Each pipeline run is a stateful process. The orchestrator tracks the state of each job for each stock (`PENDING`, `RUNNING`, `SUCCESS`, `FAILED`). A failure transitions the task to a `FAILED` state and triggers alerts.
-   **Failure Handling--**
    -   **Atomicity--** The pipeline for a given stock is treated as a transaction. A failure in any stage (`Ingestion`, `Processing`, `Prediction`) marks the entire workflow for that stock as failed for the day. Downstream jobs will only operate on data explicitly marked as successful from the prior stage.
    -   **Retries--** The orchestrator will manage a configurable retry policy (e.g., exponential backoff) for transient errors (e.g., network issues, temporary API unavailability).
    -   **Alerting--** Any job that enters a `FAILED` state after exhausting its retries will trigger an immediate alert (e.g., Slack, email) to the development team.

### 2.6. Model Registry

-   **Responsibility--** Manages the lifecycle of machine learning models. It provides a central, versioned repository for storing, tracking, and serving models.
-   **Technology--** A dedicated tool like **MLflow** is recommended.
-   **Functionality--**
    -   **Versioning--** Every trained model is saved as a new version.
    -   **Staging--** Models are tagged with stages (e.g., `staging`, `production`, `archived`).
    -   **Decoupling--** Pipeline jobs (`ProcessingJob`, `PredictionJob`) are not tied to a specific model file. Instead, they query the registry for the model currently tagged as `production`, decoupling model updates from code deployments.

### 2.7. Monitoring and Retraining Loop

-   **Responsibility--** Closes the loop from production deployment back to model development, ensuring the system adapts to changing market dynamics and prevents model drift.
-   **Components--**
    -   `PerformanceMonitoringJob`-- A scheduled job (e.g., weekly) that compares the stored predictions against actual market outcomes. It calculates key performance metrics (e.g., directional accuracy, Sharpe Ratio). If performance drops below a predefined threshold, it triggers an alert and can automatically initiate the `RetrainingJob`.
    -   `RetrainingJob`-- A job that uses the latest available data from the `Data Store` to retrain, evaluate, and validate a new version of the prediction model. If the new model outperforms the current production model on a hold-out dataset, it is registered in the **Model Registry** and can be promoted to `production`.

### 2.8. Frontend UI Module

-   **Responsibility--** Provides a user-friendly web interface for interacting with the platform.
-   **Components--** UI Components, Views/Pages, and API communication functions.

## 3. Component Interaction

### 3.1. Daily Prediction Workflow (Orchestrated)

1.  The `Pipeline Orchestrator` triggers the `IngestionJob` on a daily schedule. The run is assigned a unique ID, and its state is marked as `RUNNING`.
2.  **IngestionJob--** Fetches fresh data and writes it to a unique, timestamped location in the `Data Store` (e.g., S3). On success, it passes a *reference* (the path to the data) to the orchestrator.
3.  **ProcessingJob--** The orchestrator triggers this job with the data reference. It loads the appropriate sentiment model from the `Model Registry`, processes the data, and writes the feature-rich dataset to a new location in the `Data Store`. It passes the new reference back to the orchestrator.
4.  **PredictionJob--** The orchestrator triggers this job with the features reference. It loads the production prediction model from the `Model Registry`, runs predictions for each stock, and stores the results in the `Database`.
5.  On successful completion of the entire DAG, the orchestrator marks the daily run as `SUCCESS`.

### 3.2. Monitoring and Retraining Workflow

1.  The `Orchestrator` triggers the `PerformanceMonitoringJob` on a recurring schedule (e.g., weekly).
2.  The job queries the `Database` for predictions and actual price movements over the last period.
3.  It calculates performance metrics. If a performance threshold is breached, it sends an alert and triggers the `RetrainingJob` via the `Orchestrator`.
4.  The `RetrainingJob` loads all relevant historical data, trains a new model candidate, and evaluates it.
5.  If the candidate is superior, it is uploaded to the `Model Registry` with a new version number and can be manually or automatically promoted to the `production` stage.

## 4. Data Flow and Models

1.  **Raw Data--** JSON/Parquet files in `Data Store` (S3).
2.  **Processed Data--** A feature-engineered Pandas DataFrame per stock, stored as Parquet in `Data Store`.
3.  **Model Input--** A scaled, 3D NumPy array.
4.  **Prediction Output--** A structured object written to the `Database`.
5.  **API Response--** A JSON response served from the `Cache` or `Database`.

## 5. Technology Stack Recommendations

-   **Backend--**
    -   **Language--** Python 3.9+
    -   **API Framework--** FastAPI
    -   **Pipeline Orchestration--** **Apache Airflow** or **Dagster**. These are vastly superior to simple schedulers for data-centric DAGs, providing essential monitoring, state management, and scalability features.
-   **Machine Learning--**
    -   **Core Libraries--** TensorFlow/Keras, Scikit-learn, Pandas, NumPy.
    -   **NLP--** Hugging Face Transformers.
    -   **Model Registry--** **MLflow**.
-   **Frontend--**
    -   **Framework--** React.
    -   **State Management--** React Query or Redux Toolkit.
-   **Data Storage--**
    -   **Database--** PostgreSQL.
    -   **Cache--** Redis.
    -   **Data Store--** An object store like **Amazon S3** or GCS for decoupling pipeline jobs.
-   **Deployment & Infrastructure--**
    -   **Containerization--** Docker and Docker Compose.
    -   **CI/CD--** GitHub Actions.
    -   **Hosting--** A cloud provider (AWS, GCP, Azure).