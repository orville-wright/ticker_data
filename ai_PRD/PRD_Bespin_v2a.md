**Product Requirements Document**

**Bespin: A Personal AI Quant**

**Version:** 1.0 (Private Release)  
**Date:** October 26, 2023  
**Status:** Draft

**Table of Contents**

1. Introduction  
2. Goals and Objectives  
3. Target Audience & User Personas  
4. Proposed Solution: Bespin Overview  
5. Detailed Features & Functionalities  
6. Non-Functional Requirements  
7. Data Model (Conceptual)  
8. Integration Points  
9. Release Plan / Milestones (Conceptual for V1)  
10. Open Issues & Questions to Resolve  
11. UX Dashboard

---

**1\. Introduction**

* **1.1. Purpose of this PRD**  
  This Product Requirements Document (PRD) defines the "Bespin: A Personal AI Quant" software program, Version 1.0, intended for a private group of users. It details the program's vision, goals, target audience, features, functionalities, and non-functional requirements. This document serves as the authoritative guide for the design, development, testing, and deployment of Bespin, ensuring all stakeholders within the private user group and development team have a common understanding of the product. Bespin is designed to empower its users with advanced analytical capabilities for making timely and informed stock trading decisions.  
* **1.2. Vision for Bespin**  
  Bespin's vision is to provide its select group of private users with a potent, personal AI-driven quantitative analyst. It aims to deliver sophisticated data analysis, real-time market insights, and systematic trading approaches, enabling these users to rapidly analyze current market conditions, identify high-potential trading opportunities with the acumen of a seasoned Quant, and receive data-backed trading recommendations with enhanced speed and confidence.  
* **1.3. Scope (V1)**  
  * **Bespin V1 Will Do:**  
    * Focus on US stock markets (e.g., NYSE, NASDAQ listed securities).  
    * Real-time and near real-time data ingestion from specified public sources for intraday stock price movements, volume, and basic technicals.  
    * Automated collection of historical stock data and relevant financial news.  
    * Calculation and display of key intraday technical indicators (e.g., VWAP, intraday-tuned RSI, MACD, MAs) and Key Performance Indicators (KPIs) (e.g., sentiment analysis, technical events).  
    * Implementation of predefined, user-configurable algorithms for trade setup analysis.  
    * Provide stock trade recommendations based on the analysis, including rationale.  
    * Basic backtesting capabilities for predefined strategies.  
    * Management of credentials for accessing data sources via a simple, unencrypted credential file for V1.  
    * User-friendly dashboard for data visualization and interaction, displaying operational status of system components.  
    * Support two primary operational modes: User-defined "Private Target stock portfolio" and dynamic "Top Movers" list analysis.  
    * Data output in JSON Lines, Pandas DataFrame compatible structures, and Markdown formats where applicable.  
    * Containerized microservices for data extraction (MCP Server) and core application logic (MCP Client).  
    * Status reporting for data extraction processes into a MySQL database.  
  *   
  * **Bespin V1 Will Not Do (for this private release):**  
    * Direct, automated trade execution with brokerage accounts (recommendation and analysis only).  
    * Allow users to develop and train their own complex AI/ML models from scratch within Bespin (will utilize pre-configured or fine-tunable models).  
    * Coverage of global markets beyond the specified US markets.  
    * Analysis of complex financial instruments like options, futures, or forex (primary focus on stocks).  
    * High-Frequency Trading (HFT) execution capabilities or infrastructure.  
    * Provide guaranteed financial advice; Bespin offers data-driven analytical insights and recommendations, not guaranteed investment outcomes.  
    * Management or creation of user-defined GraphDB schemas beyond the predefined schema for news.  
    * Implement advanced security measures for the Credential Vault in V1.0 (planned for future releases).  
  *   
*   
* **1.4. Reference to Source Document**  
  The design and functional principles of Bespin are fundamentally inspired by the practices and expertise of "quantitative analyst traders" (Quants), and the premise that "Quants exhibit the highest performance stock trading financial returns." Bespin aims to encapsulate and automate key Quant tasks such as mathematical model application, statistical analysis, algorithmic thinking, data analysis (including wrangling and cleansing), backtesting, risk awareness, and leveraging financial knowledge for its private users.  
* **1.5. Glossary of Terms**  
  * **Quant:** Quantitative Analyst Trader.  
  * **Bespin:** The software product described in this PRD; "A Personal AI Quant."  
  * **Private User Group:** The select, small group of individuals for whom Bespin V1 is being developed.  
  * **Intraday:** Occurring within a single trading day.  
  * **MCP (Model Context Protocol):** A defined protocol for communication between Bespin's microservices, specifically between the Data Extraction Engines (MCP Servers) and the Bespin Core Application (MCP Client).  
  * **Data Extraction Engine:** A microservice responsible for fetching, processing, and formatting data from various sources.  
  * **JSON Lines:** A text format for storing structured data where each line is a valid JSON object.  
  * **Pandas DataFrame:** A 2-dimensional labeled data structure popular in Python for data analysis.  
  * **Pandasql:** A Python library that allows querying Pandas DataFrames using SQL syntax.  
  * **Markdown:** A lightweight markup language for creating formatted text.  
  * **API:** Application Programming Interface.  
  * **Backtesting:** Testing a trading strategy on historical data.  
  * **Technical Indicators:** Calculations based on stock data (price, volume) to predict future price movements.  
  * **KPI:** Key Performance Indicator.  
  * **GraphDB:** Graph Database (e.g., Neo4j).  
  * **Sentiment Analysis:** Analyzing text to determine underlying emotional tone.  
  * **intraday\_data\_sources.md:** Configuration file detailing data sources, API keys (references to vault), rate limits, etc.  
  * **GUI:** Graphical User Interface.  
  * **CLI:** Command Line Interface.  
  * **LLM:** Large Language Model (relevant for future sentiment analysis or interaction models).  
  * **Deno:** A JavaScript/TypeScript runtime.  
  * **Vite/Turborepo/Tailwind:** Frontend build tools/frameworks.  
* 

---

**2\. Goals and Objectives**

* **2.1. Business Goals (for Private User Group Context)**  
  * Achieve high satisfaction and regular active use of Bespin by all members of the private user group within 3 months of V1.0 delivery.  
  * Demonstrate tangible improvements in the efficiency and/or quality of trading decisions for the private user group, as self-reported or qualitatively assessed.  
  * Establish a stable and reliable V1.0 platform that serves as a foundation for future enhancements based on the private group's evolving needs and feedback.  
  * Ensure Bespin is a valuable and indispensable tool for the daily trading preparation and analysis of the private user group.  
*   
* **2.2. Product Goals**  
  * **Empower Private Users with Quant Capabilities:** Enable the private user group to perform sophisticated data analysis and apply quantitative techniques rapidly, leveraging automation.  
  * **Maximize Speed to Insight:** Deliver real-time data processing and analysis, allowing users to react swiftly to intraday market changes ("analyze what the stock market is doing right now").  
  * **Enhance Trading Decision Quality:** Provide data-driven trade recommendations and comprehensive analytical context to help the private users make more informed decisions.  
  * **Automate Intensive Pre-Trade Research:** Significantly reduce the time and effort users spend on manual data collection, cleansing, indicator calculation, and pattern searching, particularly for the specified operational modes.  
  * **Provide Actionable, Justified Recommendations:** Move beyond raw data to offer specific, actionable trade ideas based on configurable algorithmic analysis and AI-driven insights.  
  * **Facilitate Two Core Operational Modes:** Seamlessly support user workflows for analyzing both a "Private Target stock portfolio" and a dynamically generated "Top Movers" list.  
*   
* **2.3. Key Success Metrics**  
  * **User Engagement & Adoption (within the private group):**  
    * Percentage of the private user group actively using Bespin daily/weekly.  
    * Average number of analyses run per user session across both operational modes.  
    * Utilization rate of core features (Trade Setup Analyzer, Backtester, choice of operational modes).  
  *   
  * **Effectiveness of Analysis & Recommendations:**  
    * User-reported satisfaction (e.g., Likert scale survey) with the quality, timeliness, and relevance of trade recommendations.  
    * Perceived time saved in pre-trade analysis (qualitative feedback, user interviews).  
    * Number of actionable insights generated that users found valuable.  
  *   
  * **User Satisfaction (Private Group):**  
    * Direct feedback sessions indicating high overall satisfaction.  
    * Qualitative assessment of confidence in using Bespin for decision support.  
  *   
  * **System Performance & Reliability:**  
    * Median data refresh latency (from source to UI): Target \< 5 seconds for critical intraday data.  
    * End-to-end analysis time for a typical trade setup query (single stock and list): Target \< 10 seconds for single, \< 1 minute for top 20 list.  
    * System Uptime available to the private group: Target \>99.5%.  
    * Successful completion rate of data extraction and analysis jobs.  
  *   
  * **Adherence to Operational Modes:**  
    * Ease of use and effectiveness reported for both "Private Target stock portfolio" mode and "Top Movers" dynamic list mode.  
  *   
* 

---

**3\. Target Audience & User Personas**

* **3.1. Primary Users:**  
  1. **Persona: "Alex Chen" \- The Advanced Private Day Trader**  
     * **Membership:** Member of the exclusive private group for whom Bespin is developed.  
     * **Trading Style:** Highly active day trader, making multiple trades per day. Focuses on short-term momentum, technical patterns, and volume spikes in US stocks.  
     * **Experience:** 5+ years of active trading. Deeply familiar with various brokerage platforms, advanced charting software, complex technical indicators, and order flow dynamics. May have experimented with scripting or simple automation previously.  
     * **Technical Skills:** Very tech-savvy. Comfortable with complex software. Understands basic programming concepts even if not a full-time developer. Appreciates efficiency, automation, and granular control.  
     * **Goals:** To gain a significant analytical edge, execute pre-trade research at machine speed, identify subtle Quant-level signals, systematically scan for opportunities based on predefined criteria, and validate trade ideas quickly against changing market conditions.  
     * **Motivations for Bespin:** Needs a powerful, customizable tool to automate the intensive data gathering and analysis tasks of a Quant, tailored to their specific strategies. Wants to leverage AI to process more information faster and uncover patterns that are difficult to spot manually, especially for intraday movements. Needs Bespin to operate in their preferred modes (focused list vs. broad market movers).  
  2.   
*   
* **3.2. User Needs & Pain Points (for Alex Chen and similar private users):**  
  1. **Need for Extreme Speed & Real-Time Analysis:**  
     * **Quant Principle:** Algorithmic Trading, High-Frequency Data Analysis.  
     * **Pain Point:** Market dynamics change in seconds. Manual analysis across multiple potential trades or updating a "Top Movers" list is too slow, leading to missed optimal entries/exits.  
  2.   
  3. **Managing and Customizing Complex Watchlists/Scan Criteria:**  
     * **Quant Principle:** Strategy Implementation, Mathematical Model Development.  
     * **Pain Point:** Existing tools might be too generic. Needs to rapidly apply sophisticated, custom-defined (or Bespin-provided configurable) Quant logic to either a curated list of personal target stocks or a dynamically changing list of market movers.  
  4.   
  5. **Information Overload & Signal Identification:**  
     * **Quant Principle:** Data Mining, Statistical Analysis.  
     * **Pain Point:** Even for an advanced trader, synthesizing numerous data points (price, volume, indicators, news, sentiment) in real-time for multiple stocks is overwhelming. Needs AI to filter noise and highlight high-probability signals.  
  6.   
  7. **Systematic Application of Trading Strategies:**  
     * **Quant Principle:** Algorithmic Trading, Disciplined Execution.  
     * **Pain Point:** Difficulty in consistently applying complex rule-sets across all potential trades without automation. Emotional biases can still creep in.  
  8.   
  9. **Iterative Refinement of Analytical Models (Parameters):**  
     * **Quant Principle:** Mathematical Model Development, Backtesting.  
     * **Pain Point:** Needs to easily tweak parameters of analytical models/algorithms provided by Bespin and see their impact without needing to code complex systems from scratch.  
  10.   
  11. **Rapid Backtesting of Intraday Ideas:**  
      * **Quant Principle:** Backtesting.  
      * **Pain Point:** Quickly validating a new intraday idea or a tweak to an existing strategy against recent historical data is time-consuming or impossible with standard tools.  
  12.   
*   
* **3.3. User Stories (for Alex Chen):**  
  1. "As Alex, a private day trader, I want to define my 'Private Target stock portfolio' within Bespin by inputting a list of up to 50 stock symbols, and set a refresh frequency (e.g., every 30 seconds), so that Bespin continuously applies its full Quant analysis and prediction capabilities exclusively to these stocks, alerting me to setups based on my configured algorithms." (Supports: User-defined Portfolio Mode, Quant Analysis, Automation)  
  2. "As Alex, I want to activate Bespin's 'Top Movers' mode, so that it automatically identifies the top 20 stocks (gainers/losers by $, %, volume) every 60 seconds, and then immediately runs its complete Quant analysis pipeline on this dynamic list to recommend potential trades." (Supports: Dynamic List Mode, Speed, Quant Analysis)  
  3. "As Alex, when Bespin identifies a trade setup in either mode, I want to see a clear recommendation card showing the stock, direction, key supporting Quant indicators (e.g., 'VWAP hold with RSI divergence and high relative volume'), and the specific algorithm that triggered it, so that I can make a rapid, informed decision." (Supports: Actionable Recommendations, Transparency, Decision Making)  
  4. "As Alex, I want to access a simplified editor for the 5 pre-set Trade Setup Analysis algorithms, allowing me to adjust thresholds and parameters (e.g., RSI levels, MA periods for crossover logic) so that I can fine-tune Bespin's analysis to my specific intraday strategies." (Supports: Mathematical Model Parameterization, Strategy Implementation)  
  5. "As Alex, I want Bespin's prediction engine to use pandasql for its internal data manipulation on Pandas DataFrames, so that its data processing is efficient and leverages SQL-like querying capabilities, contributing to faster and more robust prediction outputs for my analysis." (Supports: Prediction Engine, Data Analysis, Technical Skills Alignment)  
  6. "As Alex, I want the Bespin UX Dashboard to display the live status of all Docker microservices (Data Extractors, Core App), which Quant algorithms are currently active and their processing time, and the status of MCP connections, so I can have full transparency into the system's operational health." (Supports: System Transparency, Reliability)  
* 

---

**4\. Proposed Solution: Bespin Overview**

* **4.1. Core Concept:**  
  Bespin: A Personal AI Quant is an integrated software solution designed to provide its private user group with the analytical power of a quantitative analyst. It achieves this by automating real-time data acquisition, applying sophisticated statistical analyses and pre-defined quantitative models (utilizing pandasql where appropriate for data manipulation within its prediction engine), identifying potential trading opportunities via configurable algorithms, and presenting these insights and recommendations in an accessible, actionable format. Bespin is architected to operate in two distinct modes—analyzing a user-defined "Private Target stock portfolio" or a dynamically generated "Top Movers" list—to cater to diverse intraday trading styles.  
* **4.2. Guiding Principles for Design:**  
  * **Embrace AI Automation for Stock Trading:** Leverage AI and algorithmic processing to automate repetitive and complex analytical tasks involved in pre-trade research.  
  * **Facilitate Deliberate AI Thought Processes for Stock Trading:** While automated, the system's logic (especially in Trade Setup Analysis) should be based on sound quantitative principles, making the "AI thinking" transparent and understandable to the user.  
  * **Provide Fast AI-Driven Analysis of Intraday Stock Data:** Engineer for minimal latency to ensure analyses are relevant to rapidly changing intraday market conditions.  
  * **Support Dual Operational Modes:**  
    * **Mode 1 (Private Target Stock Portfolio):** The user can manually input multiple individual stock symbols that they have personally chosen. Bespin will apply all of its capabilities to this list only. The user can define a frequency (e.g., every N seconds/minutes) for how long Bespin will monitor this list and re-run Quant analysis as the intraday market environment dynamically changes.  
    * **Mode 2 (Dynamic Top Movers List):** The list of stocks to analyze is dynamically and programmatically built from monitoring the top 20 stock movers gathered by the Data Extractors engines (i.e., gainers & losers by $, by %, by volume) at a user-configurable frequency (default: every 60 seconds). Bespin will build this list and then immediately apply its Quant analysis capabilities to it, continuously as the list changes.  
  *   
  * **User-Centric Customization (V1 Focused):** Allow users to tailor aspects like analysis frequency, parameters of pre-defined algorithms, and operational modes.  
  * **Transparency and Operational Visibility:** Provide users with clear insights into data sources, active processes, and system status via the dashboard.  
  * **Iterative Development for Private Group:** Design for flexibility to incorporate feedback and new requirements from the private user group in future iterations.  
*   
* **4.3. High-Level Architecture Sketch (Conceptual):**  
  Bespin will employ a microservices-based architecture using Docker containerization.  
  * **Presentation Layer:**  
    * **UX Dashboard (Web Application):** Rich, interactive GUI built with Deno/TypeScript and Vite/Turborepo/Tailwind.  
    * **Command Line Admin Tool (CLI):** For backend administration and operational tasks.  
  *   
  * **Application Layer (Bespin Core Application \- MCP Host Application \- Dockerized Microservice):**  
    * **API Gateway:** Central request entry point.  
    * **Orchestration Service:** Coordinates microservice workflows, manages operational modes (Private Target List vs. Top Movers).  
    * **User & Configuration Management Service:** Handles user preferences, algorithm configurations.  
    * **Bespin MCP Client (Model Context Protocol):** Communicates with Data Extraction Engines.  
    * **Notification Service:** (Future: For alerts; V1: For internal system events if needed).  
  *   
  * **Data Processing & Analytical Layer (Microservices \- many Dockerized):**  
    * **Data Extraction Engines (Dockerized MCP Servers):** Source-specific data fetchers/processors.  
    * **Data Aggregation & Enrichment Service:** Cleans, merges, enriches data (potentially using pandasql for DataFrame manipulations).  
    * **Technical Indicator Calculation Service:** Computes MACD, RSI, VWAP, etc.  
    * **KPI Engine:** Calculates and aggregates KPIs.  
    * **News Processing Service (includes Sentiment Analysis):** Processes news, performs NLP.  
    * **Prediction Engine Service:** Hosts AI/ML models. **Crucially, utilizes pandasql for querying and manipulating Pandas DataFrames as part of its data processing pipeline before model input or for post-processing model output.**  
    * **Trade Setup Analyzer Service:** Applies algorithms to identify trade setups.  
    * **Backtesting Service (V1 \- Simplified):** Tests strategies on historical data.  
  *   
  * **Data Storage Layer:**  
    * **Time-Series Database (e.g., InfluxDB):** For market data.  
    * **Relational Database (MySQL):** For user data, configurations, Data Extractor operational status.  
    * **News Graph Database (e.g., Neo4j):** For news relationships.  
    * **Configuration Store / Object Storage (e.g., S3 or local files):** For configs, cached data.  
    * **Service Credential Vault (Simple File \- credentials\_main.unsecure):** Unencrypted file for API keys/URLs in V1.  
    * **Alternative Credential Pool Shuffler (Simple File \- credentials\_alt\_pool.unsecure):** Unencrypted file.  
  *   
  * **External Integrations:**  
    * Financial Data Providers (APIs/Scraping).  
    * News APIs.  
  *   
* 

---

**5\. Detailed Features & Functionalities**

**5.1. Data Extraction Engines (Framework)**

* **User Problem Solved:** Automates reliable collection of diverse financial data, essential for both operational modes, saving users from manual, error-prone efforts.  
* **Detailed Description:**  
  * Each Data Extraction Engine is a Docker containerized microservice that includes an **MCP (Model Context Protocol) Server** component.  
  * The **Bespin Core Application server** (itself a separate Docker containerized microservice) runs the **Bespin MCP (Model Context Protocol) Client**.  
  * Communication between MCP Client and MCP Servers facilitates data requests and structured data delivery.  
  * **Status Reporting (to MySQL DB):** When extractors start, and during operation, they report their status. The GUI and CLI can query this.  
    * INITIALIZING, IDLE, EXTRACT\_DATA\_PENDING,  
    * EXTRACT\_DATA\_IN\_PROGRESS (Tracks: Service URL, Type of extraction Web scrape or API, Date and Time started).  
    * EXTRACT\_DATA\_COMPLETED (Tracks: Success/Fail/Errors status, Time Completed, Records fetched).  
    * DATA\_WRANGLING\_IN\_PROGRESS (Cleaning, tidying, preparing raw data).  
    * DATA\_WRANGLING\_COMPLETED.  
    * FORMAT\_STRUCTURING\_IN\_PROGRESS (Structuring cleaned data into output formats).  
    * FORMAT\_STRUCTURING\_COMPLETED.  
    * ERROR\_STATE (with error details).  
    * THROTTLED (if rate limits hit).  
  *   
  * **Extraction Methods:** Web scraping (e.g., using Python libraries like Scrapy, requests-html, BeautifulSoup4, Playwright adapted from early prototyped well working source files examples @y\_cookiemonster.py), Unofficial Web endpoints, Official APIs, Unofficial APIs (leveraging insights from @y\_topgainers.py, @y\_smallcaps.py, @y\_daylosers.py, @nasdaq\_uvoljs.py, @nasdaq\_wrangler.py).  
  * **Output Formats (via MCP transactions as structured data):**  
    * JSON Lines  
    * Pandas DataFrame (directly or easily convertible)  
    * Markdown (for human-readable summaries or specific outputs)  
  *   
  * **Configuration (intraday\_data\_sources.md or ideally YAML/JSON for easier parsing):** Contains Source Name, Base URL, Specific Endpoints, Data Types Provided, Extraction Method, API Key Reference (to Credential Vault file), Rate Limits, Request Headers/Parameters, Notes on reliability/quirks.  
*   
* **Step-by-Step User Interaction Flow (System-Level, Admin view):**  
  * Bespin Core App (Orchestrator) determines data needs based on active mode (Private Target List or Top Movers) and configured frequency.  
  * Core App (MCP Client) sends requests to relevant Data Extraction Engines (MCP Servers).  
  * Extractor retrieves credentials from Credential Vault file.  
  * Extractor fetches data, reports EXTRACT\_DATA\_IN\_PROGRESS.  
  * Extractor performs wrangling (DATA\_WRANGLING\_IN\_PROGRESS).  
  * Extractor structures data (FORMAT\_STRUCTURING\_IN\_PROGRESS).  
  * Extractor sends structured data back to Core App via MCP and reports \*\_COMPLETED status.  
  * Core App receives data for further processing.  
  * Extractor can be configured to keep extracting and updating its local datasets independently of the Bespin Core App and Client requests (like a pre-fetched cache). It may choose to use pre-fetched cache data if the date and time of the client request matches the time of the most recent locally pre-fetched dataset). Thereby avoiding a slow network transaction. The locally cached dataset can be conferred to be kept for some length of time (maximum is the full trading day). This dataset can be used for Micro-Backtesting within the current active day (i.e. today).  
*   
* **UI/UX Considerations (Admin CLI / GUI Status Panel):**  
  * Live status table of all extractors (Name, Current Status, Last Success, Last Error, Records Processed).  
  * Ability to view detailed logs per extractor.  
  * Manual trigger (for testing) for specific extractors.  
*   
* **How it Supports Techniques from Source Document:** Automates Data Analysis (collection), Data Mining, Data Wrangling, Data Cleansing, Data Sanitization, Data Normalization. Foundation for all subsequent Quant tasks.  
* **Acceptance Criteria:**  
  * Data Extraction Engines deployable as Docker containers with embedded MCP Server.  
  * Bespin Core Application includes MCP Client and communicates successfully with MCP Servers.  
  * All specified statuses reported accurately to the MySQL database.  
  * Extractors can use web scraping, official/unofficial APIs/endpoints.  
  * Data output in specified formats (JSON Lines, Pandas DataFrame, Markdown) is correctly structured.  
  * Extractors correctly parse and utilize intraday\_data\_sources.md (or chosen format).  
  * Graceful handling of data source errors, network issues, and rate limits (including use of Alternative Credentials Shuffle Pool).  
  * The system can scale to handle data extraction for the "Top Movers" list (approx. 20-40 stocks if gainers and losers combined) plus a "Private Target stock portfolio" of up to 50 stocks concurrently, respecting individual source rate limits.

**5.1.2. Data Collection: Intraday Stock Movements**

* **User Problem Solved:** Provides current price/volume for timely intraday decisions.  
* **Detailed Description:** Near real-time US stock data.  
  * **Data Points:** Ticker, Last Price, Price Change ($, %), Volume, Volume Change (delta), Timestamp, Day Open/High/Low, Prev Close.  
*   
* **UI/UX Considerations:** Clear display, color codes, sortable lists, "last updated" timestamp.  
* **How it Supports Techniques from Source Document:** Data Analysis, Algorithmic Trading inputs, Financial Knowledge.  
* **Acceptance Criteria:** All data points fetched accurately, configurable update frequency, correct calculations, standard output formats.

**5.1.3. Data Collection: Intraday Unusual Volume Movement**

* **User Problem Solved:** Helps identify stocks with significant interest or institutional activity.  
* **Detailed Description:** Identifies stocks with unusual volume vs. historical intraday norms.  
  * **Data Points/Calculations:** Ticker, Current Volume, Average Intraday Volume (vs. lookback period), Unusual Volume Ratio, Unusual Volume Percentage, Timestamp. May involve downstream "Analytical Engine."  
*   
* **UI/UX Considerations:** Clear thresholds for "unusual," visual chart indicators, alerts.  
* **How it Supports Techniques from Source Document:** Statistical Analysis, Data Analysis, Algorithmic Trading signals.  
* **Acceptance Criteria:** All data points provided accurately, correct calculations for average/ratio/percentage, system identifies high relative volume stocks.

**5.1.4. Data Collection for Intraday Stock Technical Indicators**

* **User Problem Solved:** Automates provision of data needed for technical indicator calculations.  
* **Detailed Description:** Extractors provide raw price/volume for downstream calculation service. Formulas modified for intraday relevance.  
  * **Raw Data by Extractors:** Ticker, Timestamped Intraday Bars (1-min, 5-min etc. OHLCV).  
  * **Target Indicators (calculated downstream):** Bollinger Bands, MACD, Money Flow (MFI), VWAP, OBV, RSI, Stochastic, MAs (SMA, EMA) – all with intraday-appropriate parameters.

* **UI/UX Considerations:** Clear charting, easy add/remove of indicators, customizable parameters, sensible defaults.  
* **How it Supports Techniques from Source Document:** Mathematical Model Application, Statistical Analysis, Algorithmic Trading building blocks.  
* **Acceptance Criteria:** Accurate intraday OHLCV provided, downstream service calculates all listed indicators correctly with intraday parameters, VWAP correct.

**5.1.5. Data Collection for KPI (Stock Key Performance Indicators)**

* **User Problem Solved:** Provides summarized view of stock performance and sentiment.  
* **Detailed Description:** Extractors fetch source data for downstream KPI Engine.  
  * **Extracted Data For:** Technical Events (historical price/volume), News Sentiment Analysis (raw news from 5.1.7), Analyst Ratings.  
  * **Aggregated KPIs (downstream):** Technical Events Summary, News Sentiment Score, Bearish/Bullish Sentiment, Analyst Ratings Summary (Aggregated by Today, 2-day, 5-day, 1-week, 1-month, Q, H, Y).

* **UI/UX Considerations:** Visual KPI dashboards, selectable aggregation periods, drill-down capability.  
* **How it Supports Techniques from Source Document:** Data Analysis, Statistical Analysis (sentiment), Financial Knowledge.  
* **Acceptance Criteria:** Raw data for KPIs fetched, downstream engine calculates KPIs correctly for all timeframes, sentiment scores logical, event detection accurate.

**5.1.6. Data Collection: Historical Time Series Stock Movement Data (Older than 1 day)**

* **User Problem Solved:** Provides necessary historical data for backtesting and trend analysis.  
* **Detailed Description:** Daily, weekly, monthly historical data.  
  * **Data Points:** Ticker, Date, OHLC, Adjusted Close, Volume. Derived: Price/Percentage Change, Historical Unusual Volume, Historical Technical Events.

* **UI/UX Considerations:** Clear historical charts, backtesting interface using this data.  
* **How it Supports Techniques from Source Document:** Backtesting, Statistical Analysis (time series), Mathematical Model Development.  
* **Acceptance Criteria:** Accurate historical OHLCV (adjusted) fetched for D/W/M periods (10-15 yrs), derived data calculable, efficient storage for retrieval.

**5.1.7. Data Collection: News**

* **User Problem Solved:** Timely access to market-moving news.  
* **Detailed Description:** Fetches news articles/headlines for stocks, sectors, market.  
  * **Data Points:** Ticker(s), Headline, Source, Publication Date/Time, Full Text/Summary, URL, Author, Categories.  
  * **Timeframes:** Today (frequent), Older (2-days, 1-wk, 2-wks, 1-mo, etc. up to 1-yr).

* **UI/UX Considerations:** Readable news display, source/time, filters, search, sentiment integration.  
* **How it Supports Techniques from Source Document:** Data Analysis (alternative data), Financial Knowledge, Event-driven strategies.  
* **Acceptance Criteria:** All news data points fetched, correct timeframes covered, duplicates handled, data timestamped, available for Sentiment/GraphDB.

**5.1.8\_B. Credential Vault (V1.0 \- Unsecured File Store)**

* **User Problem Solved:** Provides a centralized, simple place to store data source URLs and credentials for V1.0, without the overhead of a secure vault system for this private release.  
* **Detailed Description:**  
  * A simple, human-readable (e.g., plain text, INI, or YAML) file named credentials\_main.unsecure (or similar, clearly indicating its unsecure nature for V1).  
  * Stores entries like SOURCE\_NAME\_API\_KEY \= "key\_value", SOURCE\_NAME\_URL \= "http://...".  
  * **V1.0 Constraint:** This system provides **NO encryption, NO advanced security features, and NO access control mechanisms** beyond filesystem permissions on the machine running Bespin. This is a temporary measure for V1.0 for the private user group. Future versions will require a proper secure vault.  
  * **Functionalities:**  
    * System (Data Extractors, other services) can read entries from this file.  
    * Manual editing of this file by the user/admin to Update/Delete/Add entries.

* **Step-by-Step User Interaction Flow (Admin/User for Management):**  
  * User manually opens credentials\_main.unsecure in a text editor.  
  * User adds, modifies, or removes lines for credentials.  
  * User saves the file.  
  * Bespin services, on next credential request, read the updated file.

* **UI/UX Considerations:**  
  * No UI for this in Bespin itself for V1. Management is via direct file editing.  
  * Clear documentation must warn users about the unsecure nature of this V1.0 approach and advise on securing the host machine.

* **How it Supports Techniques from Source Document:** Facilitates Data Analysis by enabling access to data sources. (Security aspect deferred).  
* **Acceptance Criteria:**  
  * Bespin services can successfully read credentials and URLs from the specified unencrypted file.  
  * The system functions correctly when credentials in the file are updated.  
  * Documentation clearly states the unsecure nature of the V1.0 credential management and recommends securing the host environment.

**5.1.9 Alternative Credentials Shuffle Pool (V1.0 \- Unsecured File Store)**

* **User Problem Solved:** Manages rate limits and provides basic credential resilience using an alternative set of (unsecured in V1) credentials.  
* **Detailed Description:**  
  * Manages a pool of alternative credentials from another simple file, e.g., credentials\_alt\_pool.unsecure.  
  * Format similar to the main credential file.  
  * **Functionalities:**  
    * System can Read/Write/Update/Delete entries (programmatically or via admin scripts if simple, otherwise manual edit for V1). For V1, assume manual edit.  
    * Data Extractors can be directed to use alternate credentials from this pool file.  
  *   
  * **Randomizer engine algorithm (for selecting an alternative credential):**  
    * Random: Picks a random alternative key for the source.  
    * Round Robin: Cycles through available alternative keys for the source.  
    * After Primary credentials are exhausted: Only tries alternatives after the primary from credentials\_main.unsecure fails (e.g., due to rate limit error response).

* **UI/UX Considerations (Admin CLI / File Edit):**  
  * Manual editing of credentials\_alt\_pool.unsecure for V1.  
  * Configuration (e.g., in intraday\_data\_sources.md or a global config) to specify the shuffle algorithm per source or globally.  
*   
* **How it Supports Techniques from Source Document:** Improves reliability of Data Analysis by mitigating single credential failures or rate limits.  
* **Acceptance Criteria:**  
  * System can read alternative credentials from credentials\_alt\_pool.unsecure.  
  * Data Extractors can switch to using alternative credentials upon primary credential failure or by directive.  
  * The three specified shuffle algorithms (Random, Round Robin, After Primary Exhausted) are implementable and selectable.  
  * Documentation covers management of this alternative pool file.

**5.1.10 Trade Setup Analysis**

* As previously detailed. This is core to Bespin's recommendations. It must work seamlessly with both Mode 1 (Private Target List) and Mode 2 (Dynamic Top Movers).  
* Trade setup card looks like the following spreadsheet table below…

| TSLA | Symbol |  |  |  |  |  |
| ----- | ----- | :---- | ----- | ----- | ----- | ----- |
| 200 | Volume |  |  |  |  |  |
| $8.00 | **Get-In** | **BUY** | $1,600.00 | Total |  | Capital invstd |
| $15.00 | Get-Out | **SELL** | $7.00 | p/share | **$1,400.0** | **PROFIT** |
| $7.50 | **Stop-Loss** | **RISK** | \-$0.50 | p/share | \-$100.0 | @ S/LOSS |
| $0.50 | Risk/Rew | **R/R** |  |  | 6.25% | RISK % |
|  |  |  |  |  |  |  |
| $8.29 | Day | OPEN | $0.66 | BASIC gain @8% |  |  |
| $9.55 | Price | NOW | $8.95 | BASIC close @8% |  |  |
|  |  |  | 10.55 | R/R Factor \>8% |  |  |
|  |  |  | $6.05 | Profit p/share @8% |  |  |
|  |  |  |  |  |  |  |
|  | R/R ratio |  | 14 : 1 | % of capital risked |  | 5.33% |

* The Trade Setup Cards are displayed in the UX Trade Dashboard.  
* The UX has a selection option to display only cards that have been deeply analyzed by the prediction system and do meet the success criteria as a possible profitable trade, or the user can select “all Trade Setup card” to be displayed (including cards that are predicted to not be a profitable trade)  
  * The user can select how many Trade Setup Cards to display in the UX dashboard. The layout matrix is fully configurable  
  * For example, 6 (w)  x 6 (h) or 4(w) x 8(h) etc  
* The Trade setup card live prices are updated every 60 seconds, and all cell calculations are re-computed when the live data is updated.  
* Each Trade setup card can be visually collapsed down (concertina) to a 1-line header that shows  
  * Symbol, Price now, Stop/Loss exit threshold, Profit, % of capital risked

**5.1.10\_B Trade Execution (Now 5.1.10B for clarity from previous version)**

* **User Problem Solved:** Guides manual trade execution, raises awareness of day trading rules, and for this private V1, allows *programmatic execution if a suitable brokerage API is integrated by the private group's technical lead/user*.  
* **Detailed Description:**  
  * **Programmatic Trade Execution (Conditional V1 Feature):**  
    * If the private user group has a specific brokerage API they wish to integrate (e.g., Interactive Brokers, Alpaca, TDAmeritrade) and the technical expertise to manage the API keys securely *outside of Bespin's V1 unsecure credential vault*, Bespin can provide hooks or a module to send trade orders.  
    * This module would take the selected Algorithm's output (Ticker, Direction, Quantity \[user defined or default\], Order Type \[Market, Limit\], Limit Price if applicable).  
    * **Responsibility for secure API key management and brokerage integration details lies with the private user group for V1.** Bespin only provides the "send order" function.

  * **Day Trading Rules Awareness:** Information on FINRA PDT rule (3 day trades in 5 business days for accounts under $25k). UI displays this info as a reminder. Bespin will **not** track trades against this rule in V1.  
  * **Output for Manual/Programmatic Execution:** Clear display of Ticker, Direction, Algorithm, Entry, Stop-Loss (suggested), Target (suggested), Rationale from 5.1.10.

* **Step-by-Step User Interaction Flow (for Programmatic Execution, if enabled):**  
  * User reviews a Trade Setup Card.  
  * User configures trade parameters (e.g., quantity, order type) if not defaulted.  
  * User clicks an "Execute Trade" button (if programmatic execution is configured).  
  * Bespin compiles trade order details.  
  * Bespin calls the (user-group-configured) brokerage API module with order details.  
  * (Optional) Bespin displays confirmation/error from brokerage API.

* **UI/UX Considerations:**  
  * Clear "Execute Trade" button if programmatic execution is enabled.  
  * Input fields for quantity, order type, limit price.  
  * Prominent display of trade parameters & disclaimers.  
  * Simple day trade rule info displayed.

* **How it Supports Techniques from Source Document:** Strategy Implementation (semi-automated), Risk Management awareness (PDT rule), Decision-Making under pressure (by streamlining).  
* **Acceptance Criteria:**  
  * If programmatic execution is pursued:  
    * Bespin can formulate an order based on an algorithm's recommendation and user inputs.  
    * A modular interface exists for the private group to plug in their brokerage API logic.  
    * Documentation clearly states user group's responsibility for brokerage API key security and integration.  
  * Trade parameters from recommendations are clearly presented.  
  * UI includes PDT rule reminder.  
  * Clear disclaimers about trading risks.

**5.1.11. Prediction engine**

* **User Problem Solved:** Provides predictive insights, leveraging AI/ML models, to enhance the quality of trade setups.  
* **Detailed Description:**  
  * **AI Model(s) to use for predictions:** V1 starts with 1-2 pre-trained models relevant to intraday stock movements (e.g., short-term price direction probability, volatility breakout likelihood). Models are not trained within Bespin by the user.  
  * **Algorithm, methodology, process for computing a prediction:**  
    1. Relevant data (intraday prices, volumes, technical indicators, KPIs, news sentiment scores) is aggregated for a stock or list of stocks. This data is often best represented in **Pandas DataFrames**.  
    2. Feature Engineering: Raw data is transformed into features suitable for the AI model.  
    3. **Data Manipulation with pandasql:** The Prediction Engine **must utilize the pandasql Python module** to query and manipulate these Pandas DataFrames using SQL syntax. This allows for flexible and powerful data selection, aggregation, and transformation steps (e.g., SELECT feature1, AVG(feature2) FROM dataframe WHERE condition GROUP BY key) before feeding data into the ML model or for processing model outputs.  
    4. Model Execution: The engineered features are fed into the pre-trained AI/ML model.  
    5. Prediction Output: The model outputs a prediction (e.g., {ticker: "XYZ", prediction\_label: "UP\_TREND", probability: 0.72, model\_version: "v1.2"}).  
    6. This output is then consumed by the Trade Setup Analyzer service to inform its recommendations.  
  * Models are managed by the system (deployed, updated by dev team).

* **Step-by-Step User Interaction Flow (Internal):**  
  * Orchestration service requests prediction for a stock/list.  
  * Prediction Engine gathers necessary data into Pandas DataFrames.  
  * Prediction Engine uses pandasql queries to select/aggregate/transform features from DataFrames.  
  * Features are passed to the AI model.  
  * Model generates prediction.  
  * Prediction is returned to the orchestrator/Trade Setup Analyzer.

* **UI/UX Considerations:**  
  * Predictions are primarily internal inputs to the Trade Setup Analyzer.  
  * If surfaced in the UI, they should be presented with confidence scores and clear caveats.  
  * The rationale for a trade setup might state "AI Prediction: Positive Outlook (72% conf.)".

* **How it Supports Techniques from Source Document:** Mathematical Model Development (using pre-built models), Statistical Analysis (inherent in ML), Algorithmic Trading (as an input), Data Analysis (feature engineering with pandasql).  
* **Acceptance Criteria:**  
  * Prediction Engine can host and execute at least one pre-trained AI/ML model.  
  * The engine correctly ingests required input data into Pandas DataFrames.  
  * **pandasql is demonstrably used for querying and manipulating data within the Prediction Engine's workflow.**  
  * The engine outputs structured predictions in a defined format.  
  * Predictions integrate as an input signal into the Trade Setup Analyzer.  
  * Prediction latency is within acceptable limits for real-time decision support.

---

**6\. Non-Functional Requirements**

* **6.1. Performance:** P95 latencies: Critical intraday data to UI \<5s; Indicator calc \<1s; Single stock full analysis (incl. prediction) \<5s; "Top Movers" list (20 stocks) analysis \<45s; UI interactions \<1.5s. Support concurrent operations for the small private user group.  
* **6.2. Scalability:** While for a private group, architecture should allow for adding more data sources or more complex algorithms without major re-writes. Handle data volume growth for historicals.  
* **6.3. Usability:** Intuitive for the target tech-savvy private users; Efficient workflows for both operational modes; Clear presentation of complex data; Adherence to "Design with Simplicity" for user interactions.  
* **6.4. Reliability & Availability:** Target 99.5% uptime for the private group during trading hours; Data integrity is paramount; Robust error handling in data extraction and analysis; Fault isolation between microservices.  
* **6.5. Security:**  
  * **V1.0 Credential Vault is explicitly UNSECURED (plain text file).** This is a known, accepted risk for the V1.0 private release. User group is responsible for securing the host machine(s).  
  * Protection of service endpoints (e.g., internal network, simple token auth if services exposed).  
  * Minimize attack surface.  
  * Future iterations must prioritize a secure credential vault and other hardening.  
*   
* **6.6. Maintainability:** Modular code (microservices); Well-documented APIs between services; Centralized logging; Externalized configurations; CI/CD pipeline for development.  
* **6.7. Accessibility:** Standard web accessibility practices should be followed for the GUI where feasible, but not a primary driver over core functionality for V1 private release.

---

**7\. Data Model (Conceptual)**  
*(Largely similar to previous, MySQL focus confirmed)*

* **User (PrivateGroupMember):** UserID, Username (simple identifier for the private group member), Preferences\_JSON (stores mode, frequency, algo params).  
* **Stock, StockPriceData, TechnicalIndicatorValue, NewsArticle, StockNewsLink, KPI\_DataPoint, TradeSetupAlgorithmConfig, TradeRecommendation, BacktestResult:** As previously detailed.  
* **DataSourceStatus (MySQL):** StatusID, ExtractorName, ServiceURL, ExtractionType, Status, LastUpdateTimestamp, Success, ErrorMessage, RecordsProcessed.  
* **MCP\_ConnectionLog (MySQL):** LogID, Timestamp, MCPClientHost, MCPServerHost, RequestType, Status, DurationMs.  
* **QuantAlgorithmUsageLog (MySQL):** LogID, Timestamp, AlgorithmID, ExecutionTimeMs, StockCountAnalyzed, OperationalMode (TargetList/TopMovers).  
* *(No specific table for credentials as they are in flat files for V1).*

---

**8\. Integration Points**  
*(Largely similar, no ReAct for V1)*

* **8.1. LLM APIs (Future):** Post-V1 for advanced sentiment/NLP. Not core to V1 unless a very specific, simple task is identified.  
* **8.2. External Financial Data APIs, External News APIs:** As detailed, managed by intraday\_data\_sources.md and V1 unsecure credential files.  
* **8.3. Internal Microservice APIs (MCP, REST/gRPC):** For Bespin components.  
* **8.4. Database Integrations:** MySQL (primary for status, config, logs), Time-Series DB, Graph DB.  
* **8.5. (Conditional V1) Brokerage APIs:** As discussed in 5.1.10B, integration responsibility lies with the private user group. Bespin offers a hook.

---

**9\. Release Plan / Milestones (Conceptual for V1 \- Private Release)**

* **Phase 0: Foundation & Core Infrastructure (Months 1-2):** Setup architecture (Docker, Deno env), CI/CD, MySQL schema, basic Data Extractor framework with MCP, Unsecure Credential Vault file access, Admin CLI stubs.  
* **9.1. Phase 1: Core Data Pipeline & Operational Modes (Months 3-5):**  
  * V1 Data Extractors for key sources (intraday, historical, news).  
  * Status reporting to MySQL.  
  * Alternative Credential Pool logic.  
  * Indicator calculation service.  
  * Basic News Processing (sentiment if simple, GraphDB population).  
  * Implementation of Mode 1 (Private Target List) and Mode 2 (Top Movers) in Core App.  
  * Initial pandasql integration in a testbed for Prediction Engine.  
  * Simple UX Dashboard (Deno/TS \+ Vite/Turborepo/Tailwind) showing basic data and status.  
  * Internal Alpha for the private group.  
*   
* **9.2. Phase 2: Analysis, Prediction & Recommendation (Months 6-8):**  
  * KPI Engine.  
  * Prediction Engine with at least one model and full pandasql integration.  
  * Trade Setup Analyzer with 5 configurable algorithms.  
  * Backtester (simplified).  
  * UX Dashboard enhancement: Recommendation cards, algorithm editor (V1 simple), full status views.  
  * (If pursued) Brokerage API hook development.  
  * Refined Alpha/Beta testing with the private user group.  
*   
* **9.3. Phase 3: Polish, Documentation & V1 Delivery (Month 9):** Bug fixes, performance tuning based on private group feedback, usability enhancements, full documentation. **V1.0 Delivery to Private User Group.**  
* **Future Considerations (Beyond V1):** Secure Credential Vault, advanced AI/ML model integration, user-defined algorithm builder, expanded market/instrument coverage, sophisticated LLM interactions, more comprehensive brokerage integration, mobile interface.

---

**10\. Open Issues & Questions to Resolve**

* Final selection of financial data providers and assessment of their reliability/cost for the group.  
* Specific pre-trained AI models for the V1 Prediction Engine and their data requirements.  
* Detailed specification for the "simplified" algorithm editor interface in V1.  
* Clarify specific security expectations/hardening for service endpoints beyond the unencrypted V1 Credential Vault, even for internal use.  
* Final decision on **Vite vs. Turborepo vs. Tailwind** for the UX Dashboard frontend stack (or a combination). User group/dev lead preference?  
* Define exact schema/format for intraday\_data\_sources.md (recommend YAML or JSON over Markdown for parsing).  
* Scope and priority of the (conditional) programmatic trade execution feature for V1.  
* Specific metrics to be logged for QuantAlgorithmUsageLog and MCP\_ConnectionLog.  
* Error handling and retry strategies for data extraction and processing.

---

**11\. UX Dashboard**

* **Technology Stack Priority:**  
  * **Runtime Engine & Language:** Deno and TypeScript.  
  * **Frontend Build Tool/Framework:** Decision to be finalized between **Vite, Turborepo, or Tailwind CSS** (or combination, e.g., Vite \+ Tailwind). Vite is often favored for speed and ease of use with TS. Turborepo for monorepo management if complexity grows. Tailwind for utility-first CSS.  
  * **Backend Database (for dashboard-specific data & system status):** MySQL.  
*   
* **Guiding Principle:** Initial simple dashboard for V1, focusing on critical information and functionality. Can be expanded iteratively.  
* **Key Display Components & Features:**  
  * **Main View Tabs/Sections:** Overview, Private Target List Analyzer, Top Movers Analyzer, Stock Detail, News, Settings.  
  * **UX Card: Computed Trade Setup for possible trades:** As detailed previously (Ticker, Direction, Rationale, Algo, Key Data). Prominently displayed when a new setup is identified.  
  * **Operational Mode Control:** Clear toggle or selection for Mode 1 (Private Target List) vs. Mode 2 (Top Movers). Input for stock symbols for Mode 1\. Configuration for refresh frequencies for both modes.  
  * **Current Analysis Context:** Display which data source(s) were used to create the stock list and dataset currently being analyzed by Bespin (e.g., "Source: YahooFinance Top Gainers \- Updated: 10:35:12 AM").  
  * **System Status Panel:**  
    * **Docker Microservices Status:** Table/list showing status of key microservices (e.g., DataExtractor\_Yahoo, DataExtractor\_NewsAPI, BespinCoreApp, PredictionEngine) \- Status (Running, Degraded, Stopped), Last Heartbeat. Queried from a health check endpoint or service discovery.  
    * **Quant Algorithms Usage:** Display which of the 5 Trade Setup Analysis algorithms are currently active/enabled. For recent analyses, show processing time per algorithm or number of stocks it evaluated (from QuantAlgorithmUsageLog).  
    * **MCP Connections Status:** Table/list showing active/idle MCP connections. Columns: MCP Server (Extractor Name), MCP Client (Core App), Status (Active, Idle, Error), Date/Time Last Used, Last Transaction Type (from MCP\_ConnectionLog).  
  *   
  * **Data Display:**  
    * Tables for stock lists (Movers, Target List) with key intraday data (Price, %, Vol, VWAP).  
    * Simple charts for selected stocks (Price, Volume, key TAs).  
  *   
  * **Day Trading Rules Reminder:** Static text block displaying FINRA PDT rule information. "This is not financial advice. You are responsible for tracking your trades."  
  * **(Future/Simple V1) Algorithm Parameter Editor:** Interface to view and adjust parameters for the 5 pre-set Trade Setup Analysis algorithms.  
  * **Log Viewer (Simple):** Access to summarized logs from key services, especially errors.  
*   
* **User Interaction Flow Highlights for Dashboard:**  
  * User logs in/accesses dashboard.  
  * User selects operational mode (Target List or Top Movers).  
    * If Target List, inputs/manages their list of symbols and monitoring frequency.  
    * If Top Movers, confirms/adjusts refresh frequency.  
  *   
  * Bespin starts analysis in the background.  
  * Dashboard updates with:  
    * Real-time data for displayed stocks.  
    * System status (Docker, MCP, Algos).  
    * Newly identified Trade Setup Cards.  
  *   
  * User clicks on a Trade Setup Card to see details.  
  * User interacts with charts, news, or other data relevant to the setup.  
  * (If programmatic execution enabled and configured) User may initiate a trade.  
*   
* **Acceptance Criteria:**  
  * Dashboard built using Deno/TypeScript and the chosen frontend tool (Vite/Turborepo/Tailwind).  
  * All specified UX cards and status displays are implemented and correctly show data from backend services/MySQL.  
  * User can select and configure both operational modes.  
  * Dashboard is responsive and updates key information in near real-time.  
  * The initial version is simple but functional, providing core insights and controls to the private user group.