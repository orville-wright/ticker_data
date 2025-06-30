# Pseudocode: get_prediction

This document outlines the detailed, language-agnostic pseudocode for the `get_prediction` function. This function is responsible for retrieving the latest prediction for a given stock symbol, utilizing a cache for performance.

## Function: `get_prediction`

**Signature:** `get_prediction(symbol: string) -> dictionary`

**Description:** Orchestrates fetching the latest pre-computed prediction for a given stock from a cache first, and then from a database if not found in the cache.

---

### **1. Initialization and Input Validation**

-   **TDD Anchor:** `TEST behavior for invalid symbol format`
    -   **Behavior:** Should handle poorly formatted symbols gracefully.
    -   **Setup:** None.
    -   **Action:** Call `get_prediction` with a symbol like " aApL ".
    -   **Assert:** The function correctly sanitizes the symbol to "AAPL" before processing.

```pseudocode
FUNCTION get_prediction(symbol):
    // Sanitize the input symbol to a consistent format
    sanitized_symbol = CONVERT_TO_UPPERCASE(TRIM_WHITESPACE(symbol))

    IF sanitized_symbol is empty or invalid THEN
        RETURN {error: "Invalid symbol provided", status_code: 400}
    END IF
```

---

### **2. Cache Lookup**

-   The system first attempts to retrieve the prediction from a fast in-memory cache (like Redis) to minimize database load and improve response time.

-   **TDD Anchor:** `TEST behavior for prediction found in cache`
    -   **Behavior:** Should return the prediction data directly from the cache without querying the database.
    -   **Setup:** Pre-populate the cache with a sample prediction for "AAPL". Mock the database connection to fail or be ignored.
    -   **Action:** Call `get_prediction("AAPL")`.
    -   **Assert:** The returned data matches the cached sample and the database is not queried.

```pseudocode
    // Attempt to get the prediction from the cache
    cached_prediction = Cache.get(sanitized_symbol)

    IF cached_prediction is not NULL THEN
        // If found, return the cached result immediately
        RETURN cached_prediction
    END IF
```

---

### **3. Database Query (Cache Miss)**

-   If the prediction is not in the cache, the function queries the primary database for the most recent prediction record for the given symbol.

-   **TDD Anchor:** `TEST behavior for prediction found in database`
    -   **Behavior:** Should retrieve the prediction from the database when it's not in the cache.
    -   **Setup:** Ensure the cache is empty for "AAPL". Populate the database with a sample prediction for "AAPL".
    -   **Action:** Call `get_prediction("AAPL")`.
    -   **Assert:** The returned data matches the database record.

```pseudocode
    // If not in cache, query the database
    // The query should order by timestamp descending and take the first result
    db_prediction_record = Database.query("SELECT * FROM predictions WHERE symbol = ? ORDER BY timestamp DESC LIMIT 1", sanitized_symbol)
```

---

### **4. Handling Database Results**

-   The function processes the result from the database. If a record is found, it's formatted, cached for future requests, and returned. If not, an error is returned.

-   **TDD Anchor:** `TEST behavior for prediction not found anywhere`
    -   **Behavior:** Should return a "not found" error if the symbol does not exist in the cache or the database.
    -   **Setup:** Ensure the cache and database are both empty for the specified symbol (e.g., "UNKNOWN").
    -   **Action:** Call `get_prediction("UNKNOWN")`.
    -   **Assert:** The function returns an error structure with a 404 status code.

-   **TDD Anchor:** `TEST behavior for caching after database hit`
    -   **Behavior:** Should store the retrieved database record in the cache.
    -   **Setup:** Ensure cache is empty. Populate the database with a prediction for "MSFT".
    -   **Action:** Call `get_prediction("MSFT")`.
    -   **Assert:** After the call, the cache now contains the prediction for "MSFT".

```pseudocode
    IF db_prediction_record is not NULL THEN
        // Format the database record into the required API response structure
        prediction_response = {
            "symbol": db_prediction_record.symbol,
            "name": get_stock_name(db_prediction_record.symbol), // Assumes a helper to get full name
            "signal": db_prediction_record.signal,
            "confidence": db_prediction_record.confidence,
            "timestamp": db_prediction_record.timestamp
        }

        // Store the newly fetched result in the cache for subsequent requests
        // Set a Time-To-Live (TTL) to ensure data freshness (e.g., 1 hour)
        Cache.set(sanitized_symbol, prediction_response, ttl=3600)

        RETURN prediction_response
    ELSE
        // If no prediction exists in the database for this symbol
        RETURN {error: "Prediction not found for symbol", status_code: 404}
    END IF

END FUNCTION
```

### **Helper Function Stub**

-   A helper function is assumed to exist for retrieving a stock's full name based on its symbol.

```pseudocode
FUNCTION get_stock_name(symbol):
    // This function would query a 'stocks' table or a similar data source
    // to find the company name associated with the ticker symbol.
    // Returns the name as a string or an empty string if not found.
    ...
END FUNCTION