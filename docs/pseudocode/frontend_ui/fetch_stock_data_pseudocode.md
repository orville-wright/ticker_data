# Pseudocode: fetchStockData for StockDetailPage

## 1. Component Context

-   **View:** `StockDetailPage`
-   **Associated Route:** `/stock/<symbol>`
-   **Purpose:** To fetch and display detailed prediction data for a specific stock symbol retrieved from the URL.

## 2. State Variables

-   `stockData` (Object): Stores the prediction data fetched from the API. Defaults to `NULL` or an empty object.
    -   Example structure: `{ "symbol": "AAPL", "signal": "BUY", "confidence": 85.5, "timestamp": "2023-10-27T12:00:00Z", "isOnWatchlist": true }`
-   `isLoading` (Boolean): Flag to indicate if the data fetching process is in progress. Defaults to `TRUE` on initial load.
-   `error` (String): Stores an error message if the API call fails. Defaults to `NULL` or an empty string.

## 3. Function: `onMount` (Lifecycle Hook)

This function is automatically invoked when the `StockDetailPage` component is first rendered.

```plaintext
FUNCTION onMount()
    // TEST: Behavior for triggering data fetch on component load
    // ACTION: Render the StockDetailPage component for a specific route, e.g., "/stock/AAPL".
    // ASSERT: The fetchStockData function should be called.
    CALL fetchStockData()
ENDFUNCTION
```

## 4. Function: `fetchStockData`

This function handles the logic for retrieving the stock prediction data from the backend API.

```plaintext
FUNCTION fetchStockData()
    // Use a TRY...CATCH...FINALLY block to manage states gracefully.
    TRY
        // 1. Set initial state for loading
        SET isLoading TO TRUE
        SET error TO NULL

        // 2. Get the stock symbol from the page's URL parameter
        // For example, from "/stock/AAPL", extract "AAPL"
        CONSTANT symbol = extractSymbolFromURL()

        // TEST: Behavior for handling a missing or invalid symbol from the URL.
        // ACTION: Navigate to a URL with a missing or malformed symbol (e.g., "/stock/").
        // ASSERT: The function should set an appropriate error state and not make an API call.
        IF symbol IS NULL OR EMPTY THEN
            SET error TO "Stock symbol is missing from the URL."
            SET isLoading TO FALSE
            RETURN
        ENDIF

        // 3. Make the API call
        // The 'await' keyword indicates an asynchronous operation.
        CONSTANT response = await FETCH_API(GET, "/api/stocks/" + symbol + "/prediction")

        // TEST: Behavior for a successful API response (Happy Path).
        // SETUP: Mock the API to return a 200 OK status with valid stock data for "AAPL".
        // ACTION: Trigger fetchStockData.
        // ASSERT: The 'stockData' state is updated with the mock data, and 'isLoading' is false.
        IF response.status IS 200 THEN
            // Update state with the fetched data
            CONSTANT data = parseJSON(response.body)
            SET stockData TO data
        ELSE
            // TEST: Behavior for a "Not Found" API response (e.g., 404).
            // SETUP: Mock the API to return a 404 status for an invalid symbol like "INVALID".
            // ACTION: Trigger fetchStockData for "INVALID".
            // ASSERT: The 'error' state is set to a "not found" message, and 'isLoading' is false.
            SET error TO "Could not find prediction data for symbol: " + symbol
            SET stockData TO NULL
        ENDIF

    CATCH apiError
        // TEST: Behavior for a generic server error (e.g., 500).
        // SETUP: Mock the API to return a 500 Internal Server Error.
        // ACTION: Trigger fetchStockData.
        // ASSERT: The 'error' state is set to a generic failure message, and 'isLoading' is false.
        SET error TO "An error occurred while fetching stock data."
        SET stockData TO NULL
        LOG "API Error:" + apiError // Log the actual error for debugging

    FINALLY
        // 4. Final state update
        // This block executes regardless of success or failure.
        SET isLoading TO FALSE
    ENDFINALLY
ENDFUNCTION