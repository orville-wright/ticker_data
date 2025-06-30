# Mutual Understanding Document

## 1. Project Overview

This document outlines the project to create an AI-powered platform designed to help individual retail investors make more informed decisions. The platform will analyze historical market data and real-time social media sentiment to predict market trends for specific stocks. The core output will be a clear, actionable signal, helping users navigate the overwhelming volume of market information.

## 2. Problem Statement

**Current State:** Individual retail investors are at a disadvantage due to an overwhelming amount of market data, financial news, and social media "noise." It is practically impossible for a human to process this volume of information effectively to make timely, data-driven investment decisions.

**Future State:** The platform will provide users with a clear, concise, and data-driven signal ("buy," "sell," or "hold") for stocks they are interested in. This will empower them to cut through the noise and make decisions based on sophisticated, AI-driven analysis that was previously only available to large institutions.

## 3. Stakeholder Analysis

The primary users and stakeholders for this platform are:

*   **Individual Retail Investors:** Individuals who actively manage their own stock portfolios and are looking for tools to improve their decision-making process. They are typically tech-savvy but may not have deep expertise in data science or quantitative analysis.

## 4. User Stories & Feature Prioritization (MoSCoW)

### Must-Haves (Essential for MVP)
*   **US-1:** As an investor, I want to see a clear "buy," "sell," or "hold" signal for specific stocks, along with a confidence score, so I can make a quick and informed decision.
*   **US-2:** As an investor, I want to be able to search for any stock and add it to a personalized watchlist so that I can track the predictions for the assets I care about.

### Should-Haves (Important, but not for initial launch)
*   **US-3:** As an investor, I want to see the key factors (e.g., top news headlines, sentiment trends) that influenced a prediction so I can understand the reasoning behind the signal.

### Could-Haves (Desirable if time and resources permit)
*   **US-4:** As an investor, I want to be able to back-test the AI's historical prediction accuracy so I can build trust in the model's performance.

## 5. SMART Success Criteria

The ultimate success of the project will be measured by the functional performance of its core feature:

*   **Specific:** Achieve a high degree of accuracy in predicting the direction of a stock's price movement.
*   **Measurable:** The model must achieve **70% accuracy**.
*   **Achievable:** This target is considered challenging but achievable with high-quality data and a robust model.
*   **Relevant:** Predictive accuracy is the core value proposition for the user.
*   **Time-bound:** This accuracy will be measured over the first **6 months** following the public launch, evaluated on a rolling basis across the user's watchlist stocks within a **5-day prediction window**.

## 6. Assumptions & Dependencies

*   **Assumption:** The platform will be able to legally and ethically provide predictive signals without it constituting financial advice.
*   **Dependency:** The project is critically dependent on securing access to clean, reliable, and affordable APIs for both historical stock data and real-time social media sentiment feeds.