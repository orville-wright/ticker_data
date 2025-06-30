# Constraints and Anti-Goals

This document outlines the specific constraints, boundaries, and explicit anti-goals for the AI-powered market prediction platform. Adhering to these is critical for maintaining focus and ensuring project success.

## 1. Technical Constraints

*   **Programming Language (Model):** The core machine learning model for predictions **must** be developed in Python.
*   **Libraries (Model):** The model **must** utilize well-established machine learning libraries, specifically from the TensorFlow or PyTorch ecosystems.
*   **Data Ingestion:** The system must be able to process data efficiently enough to provide fresh signals at least one hour before market open each trading day.

## 2. Business Constraints

*   **Target Audience:** The platform is exclusively for individual retail investors. The user interface, features, and complexity must be appropriate for this audience.
*   **Scope:** The initial version of the platform will be a purely informational tool. It will not provide financial advice or automated trading.

## 3. Anti-Goals (What We Will Not Do)

*   **No Other Asset Classes:** The platform **will not** cover any assets other than stocks (e.g., no cryptocurrencies, forex, commodities, or options) in its initial versions.
*   **No Financial Advice:** The platform **will not** provide personalized financial advice, portfolio management, or recommendations tailored to an individual's financial situation. All outputs are to be presented as data-driven predictions, not advice.
*   **No Automated Trading:** There **will not** be any functionality for automated trading or direct integration with brokerage accounts for trade execution.
*   **No Social Features:** The platform **will not** include social networking features, such as sharing watchlists, comments, or user-to-user discussions.

## 4. Primary Identified Risk

*   **Data Quality and Availability:** The most significant risk to the project is the challenge of securing and maintaining access to high-quality, clean, reliable, and timely data for both historical stock prices and real-time social media sentiment. The project's success is fundamentally dependent on the quality of this input data.