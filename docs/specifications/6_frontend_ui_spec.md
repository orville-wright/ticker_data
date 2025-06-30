# Specification: Frontend UI Components

This document provides the technical specifications for the frontend user interface. It defines the necessary components, their properties (props), state, and the functions they will perform. This specification assumes a modern JavaScript framework like React, Vue, or Svelte. The examples will use React-style syntax.

## 1. Overview

The frontend will be a single-page application (SPA) that interacts with the backend API to display stock predictions and manage watchlists. The UI will be composed of several modular components, each with a specific responsibility.

---

## 2. Core UI Components

### 2.1. Component: `StockSearchBar`

-   **Description:** A search bar that allows users to find stocks.
-   **State:**
    -   `query` (str): The current text entered by the user.
    -   `suggestions` (list[dict]): A list of stock suggestions from the API.
    -   `isLoading` (bool): A flag to indicate when an API call is in progress.
-   **Props:**
    -   `onStockSelect` (function): A callback function that is invoked when a user selects a stock from the suggestions. It receives the stock symbol as an argument.
-   **Functions/Methods:**
    -   `handleInputChange(event)`: Updates the `query` state and debounces a call to `fetchSuggestions`.
    -   `fetchSuggestions()`: Calls the backend API `GET /api/stocks/search` with the current query and updates the `suggestions` state.
    -   `handleSelect(symbol)`: Calls the `onStockSelect` prop with the selected symbol.
-   **TDD Anchor/Pseudocode Stub:**
    ```javascript
    // TEST: StockSearchBar component
    // BEHAVIOR: Should fetch and display suggestions as user types.
    // SETUP: Render the component. Mock the API call to return sample suggestions.
    // ACTION: Simulate user typing "APP" into the search input.
    // ASSERT: The component should display a list containing "AAPL - Apple Inc.".
    ```

### 2.2. Component: `PredictionDisplay`

-   **Description:** A component to prominently display the prediction signal for a stock.
-   **Props:**
    -   `signal` (str): The prediction signal ('BUY', 'SELL', 'HOLD').
    -   `confidence` (number): The confidence score (0-100).
    -   `timestamp` (str): The ISO 8601 timestamp of when the signal was generated.
-   **Logic:**
    -   Conditionally applies styling (e.g., color) based on the `signal` prop.
    -   Renders the confidence score in a visual gauge or progress bar.
    -   Formats the `timestamp` for display.

### 2.3. Component: `WatchlistButton`

-   **Description:** A button to add or remove a stock from the user's watchlist.
-   **State:**
    -   `isOnWatchlist` (bool): Tracks whether the stock is currently on the watchlist.
    -   `isLoading` (bool): For API call in-progress state.
-   **Props:**
    -   `symbol` (str): The stock symbol this button corresponds to.
    -   `initialIsOnWatchlist` (bool): The initial state of the button.
-   **Functions/Methods:**
    -   `handleClick()`:
        -   If `isOnWatchlist` is false, calls `addToWatchlist`.
        -   If `isOnWatchlist` is true, calls `removeFromWatchlist`.
    -   `addToWatchlist()`: Calls the backend API `POST /api/watchlist` and updates state on success.
    -   `removeFromWatchlist()`: Calls the backend API `DELETE /api/watchlist/<symbol>` and updates state on success.

### 2.4. Component: `WatchlistTable`

-   **Description:** Displays the user's watchlist in a table or grid.
-   **Props:**
    -   `watchlistItems` (list[dict]): A list of objects, each representing a stock on the watchlist with its latest signal.
-   **Logic:**
    -   Maps over the `watchlistItems` prop to render a `WatchlistRow` for each item.
    -   Displays a message if the `watchlistItems` list is empty.

### 2.5. Component: `WatchlistRow`

-   **Description:** A single row in the `WatchlistTable`.
-   **Props:**
    -   `item` (dict): The stock object containing symbol, name, signal, and confidence.
    -   `onRemove` (function): Callback function to trigger removal from the watchlist, passing the symbol.

---

## 3. Page-Level Components / Views

### 3.1. View: `StockDetailPage`

-   **Description:** The main page for viewing details and the prediction for a single stock.
-   **State:**
    -   `stockData` (dict): The prediction data for the stock, fetched from the API.
    -   `isLoading` (bool): Loading state for the API call.
    -   `error` (str): Error message if the API call fails.
-   **Route:** `/stock/<symbol>`
-   **Composition:**
    -   Uses the `PredictionDisplay` component.
    -   Uses the `WatchlistButton` component.
-   **Functions/Methods:**
    -   `fetchStockData()`: On component mount, gets the symbol from the URL and calls the backend API `GET /api/stocks/<symbol>/prediction`. Updates state with the result.

### 3.2. View: `WatchlistPage`

-   **Description:** The dashboard view for the user's entire watchlist.
-   **State:**
    -   `watchlist` (list[dict]): The list of stocks on the user's watchlist.
    -   `isLoading` (bool): Loading state.
-   **Route:** `/watchlist`
-   **Composition:**
    -   Uses the `WatchlistTable` component.
-   **Functions/Methods:**
    -   `fetchWatchlist()`: On component mount, calls the backend API `GET /api/watchlist` and populates the `watchlist` state.
    -   `handleRemoveItem(symbol)`: A function passed to `WatchlistTable` that calls the `DELETE` API endpoint and updates the `watchlist` state to reflect the removal.