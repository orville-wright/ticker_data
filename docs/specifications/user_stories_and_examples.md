# User Stories and Examples

This document provides a comprehensive set of granular user stories, complete with detailed scenarios and acceptance criteria. It is based on the high-level user stories defined in the Mutual Understanding Document and serves as a foundational input for the specification and testing phases.

---

## 1. Core Prediction and Watchlist Features (MVP)

This section breaks down the "Must-Have" user stories (US-1 and US-2) into more detailed components.

### 1.1. Story: Searching for a Stock

*   **Parent Story:** US-1, US-2
*   **As a** retail investor,
*   **I want to** search for a stock by its ticker symbol (e.g., "AAPL") or company name (e.g., "Apple"),
*   **so that** I can find the specific stock I'm interested in and view its prediction signal.

#### Example Scenario

1.  **User Action:** Sarah, a retail investor, logs into the platform. She sees a prominent search bar at the top of the page.
2.  **Input:** She types "MSFT" into the search bar.
3.  **System Response:** As she types, a dropdown list appears showing potential matches. "MSFT - Microsoft Corp." is at the top of the list.
4.  **User Action:** Sarah clicks on "MSFT - Microsoft Corp." from the dropdown.
5.  **System Response:** The platform navigates her to the dedicated stock prediction page for Microsoft (MSFT).

#### Acceptance Criteria

*   **AC1:** The UI must contain a search bar that is easily accessible from the main dashboard/view.
*   **AC2:** The search functionality must support queries by both ticker symbol and company name.
*   **AC3:** The system must provide real-time search suggestions in a dropdown list as the user types (autocomplete).
*   **AC4:** Selecting a stock from the search results must navigate the user to that stock's specific prediction page.
*   **AC5:** If no stock matches the search query, the system must display a clear "No results found" message.
*   **AC6:** The search must only return results for publicly traded stocks, as per the project constraints (no crypto, forex, etc.).

### 1.2. Story: Viewing a Prediction Signal

*   **Parent Story:** US-1
*   **As a** retail investor,
*   **I want to** see a clear "buy," "sell," or "hold" signal and a corresponding confidence score on the stock's prediction page,
*   **so that** I can quickly assess the AI's prediction for that stock.

#### Example Scenario

1.  **Context:** Following the search scenario, Sarah is now on the prediction page for MSFT.
2.  **System Display:** At the top of the page, she sees a large, clear visual element that prominently displays the signal.
3.  **Content:**
    *   **Signal:** "BUY" (displayed in green).
    *   **Confidence Score:** A progress bar or gauge shows "82% Confidence."
    *   **Timestamp:** A label indicates "Signal generated today at 7:30 AM EST."
4.  **User Interpretation:** Sarah immediately understands that the AI's prediction for MSFT is positive, with a high degree of confidence, and that the signal is fresh for the current trading day.

#### Acceptance Criteria

*   **AC1:** The prediction page for a given stock must display one of three unambiguous signals: "Buy," "Sell," or "Hold."
*   **AC2:** The signal must be visually distinct (e.g., using color-coding: green for Buy, red for Sell, gray for Hold).
*   **AC3:** A confidence score, represented as a percentage (0-100%), must be displayed alongside the signal.
*   **AC4:** The confidence score must be visualized (e.g., a radial gauge, progress bar, or similar graphic).
*   **AC5:** The page must display a timestamp indicating when the signal was generated, confirming its relevance for the current trading day.
*   **AC6:** The signal and confidence score must be the most prominent elements on the page.

### 1.3. Story: Adding a Stock to the Watchlist

*   **Parent Story:** US-2
*   **As a** retail investor,
*   **I want to** add a stock to my personal watchlist directly from its prediction page,
*   **so that** I can easily track its future predictions without having to search for it every time.

#### Example Scenario

1.  **Context:** Sarah is on the MSFT prediction page and decides she wants to track it.
2.  **User Action:** She sees an "Add to Watchlist" button (perhaps with a star or plus icon) near the stock's name. She clicks it.
3.  **System Response:**
    *   The button immediately changes to "On Watchlist" and its icon changes (e.g., the star becomes filled in).
    *   A temporary confirmation message appears: "MSFT has been added to your watchlist."
4.  **User Interpretation:** Sarah knows her action was successful and that MSFT will now appear in her watchlist.

#### Acceptance Criteria

*   **AC1:** An "Add to Watchlist" button/control must be present on every stock prediction page.
*   **AC2:** Clicking the "Add to Watchlist" button must add the stock to the user's personalized watchlist.
*   **AC3:** After a stock is added, the button's state must change to indicate the stock is already on the watchlist (e.g., the button becomes disabled or its text changes to "On Watchlist").
*   **AC4:** The system must provide clear, non-intrusive feedback to confirm the action was successful (e.g., a toast notification).
*   **AC5:** The user must not be able to add the same stock to the watchlist more than once.

### 1.4. Story: Viewing the Watchlist

*   **Parent Story:** US-2
*   **As a** retail investor,
*   **I want to** view all the stocks on my watchlist on a dedicated dashboard,
*   **so that** I can see the latest prediction signals for all my tracked stocks in one place.

#### Example Scenario

1.  **User Action:** After adding MSFT, Sarah navigates to her watchlist page via a "Watchlist" link in the main navigation.
2.  **System Display:** The watchlist page displays a table or a grid of cards. Each row/card represents a stock she has added.
3.  **Content:** The table has columns for:
    *   Ticker Symbol (e.g., "AAPL," "MSFT," "GOOGL")
    *   Company Name (e.g., "Apple Inc.," "Microsoft Corp.," "Alphabet Inc.")
    *   Today's Signal (e.g., "Hold," "Buy," "Sell") with appropriate color-coding.
    *   Confidence Score (e.g., "65%," "82%," "75%")
    *   A "Remove" button for each stock.
4.  **User Interpretation:** Sarah can now scan the list and quickly get the day's predictions for all the stocks she cares about.

#### Acceptance Criteria

*   **AC1:** There must be a dedicated "Watchlist" page or dashboard accessible from the main navigation.
*   **AC2:** The watchlist must display a list of all stocks the user has personally added.
*   **AC3:** For each stock on the list, the following information must be displayed: Ticker Symbol, Company Name, the latest Signal ("Buy"/"Sell"/"Hold"), and the Confidence Score.
*   **AC4:** The signal and confidence score shown on the watchlist must match the information on the individual stock's prediction page for that day.
*   **AC5:** If the watchlist is empty, a message should guide the user to search for stocks and add them.

### 1.5. Story: Removing a Stock from the Watchlist

*   **Parent Story:** US-2
*   **As a** retail investor,
*   **I want to** be able to remove a stock from my watchlist,
*   **so that** I can keep my tracked assets relevant to my current interests.

#### Example Scenario

1.  **Context:** A few weeks later, Sarah decides she is no longer interested in tracking GOOGL.
2.  **User Action:** She navigates to her watchlist page and finds the row for "GOOGL." She clicks the "Remove" button (perhaps represented by a trash can icon) in that row.
3.  **System Response:**
    *   A confirmation dialog appears: "Are you sure you want to remove GOOGL from your watchlist?"
    *   Sarah clicks "Confirm."
    *   The row for GOOGL is immediately removed from her watchlist view.
    *   A temporary notification appears: "GOOGL has been removed from your watchlist."
4.  **User Interpretation:** Sarah is confident that the stock has been removed and her watchlist is now up-to-date.

#### Acceptance Criteria

*   **AC1:** Each stock listed on the watchlist page must have a "Remove" control.
*   **AC2:** Clicking the "Remove" control must trigger a confirmation prompt to prevent accidental deletion.
*   **AC3:** Upon confirmation, the stock must be permanently removed from the user's watchlist data.
*   **AC4:** The UI must update immediately to reflect the removal of the stock from the list.
*   **AC5:** The "Add to Watchlist" button on the removed stock's prediction page must revert to its original state, allowing the user to add it back if they choose.