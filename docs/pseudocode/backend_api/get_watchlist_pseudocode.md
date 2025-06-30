# Pseudocode: get_watchlist

## Function Signature

`FUNCTION get_watchlist(user_id AS INTEGER) RETURNS LIST<DICTIONARY>`

## Description

This function retrieves the watchlist for a given user, including the latest prediction signal for each stock on the list. It corresponds to the `GET /api/watchlist` endpoint, which requires authentication.

## SPARC Design Principles

- **Specification:** The pseudocode is based on the requirements outlined in [`docs/specifications/5_backend_api_spec.md`](docs/specifications/5_backend_api_spec.md:79-102).
- **Architecture:** This function will interact with the database to fetch user-specific data and will likely call another function (`get_prediction`) to retrieve prediction data, promoting modularity.
- **Refinement:** TDD anchors are included to ensure all logical paths are testable and behavior is verifiable.
- **Completion:** The output is a clear, language-agnostic blueprint for implementation.

---

## Logic

```plaintext
FUNCTION get_watchlist(user_id)
    -- TEST get_watchlist_db_error_on_connect
    -- BEHAVIOR: Should handle database connection errors gracefully.
    -- SETUP: Configure the database mock to raise a connection error.
    -- ACTION: Call the function with any user_id.
    -- ASSERT: The function returns an empty list and logs the error.
    TRY
        -- Get the list of stock symbols for the given user from the database.
        -- This assumes a 'watchlist' table with 'user_id' and 'symbol' columns.
        watchlist_symbols = DATABASE_QUERY("SELECT symbol FROM watchlist WHERE user_id = :user_id", user_id)

        -- TEST get_watchlist_for_empty_watchlist
        -- BEHAVIOR: Should return an empty list for a user with no stocks in their watchlist.
        -- SETUP: Ensure the database mock returns an empty list for the user's watchlist query.
        -- ACTION: Call the function with the test user's ID.
        -- ASSERT: The function returns an empty list [].
        IF watchlist_symbols IS EMPTY THEN
            RETURN []
        END IF

        -- Initialize a list to hold the final results.
        full_watchlist = NEW LIST

        -- TEST get_watchlist_success
        -- BEHAVIOR: Should return a list of stocks with their latest predictions.
        -- SETUP:
        --   1. Mock the watchlist DB query to return ['AAPL', 'MSFT'].
        --   2. Mock the stock details DB query to return name for 'AAPL' and 'MSFT'.
        --   3. Mock the get_prediction function to return valid prediction data for both symbols.
        -- ACTION: Call the function with the test user's ID.
        -- ASSERT: The returned list contains two dictionaries, each with symbol, name, and prediction data.
        FOR EACH symbol IN watchlist_symbols
            -- Fetch stock details (like the company name) from a 'stocks' table.
            stock_details = DATABASE_QUERY("SELECT name FROM stocks WHERE symbol = :symbol", symbol)

            -- Fetch the latest prediction for the stock. This could be a direct DB query
            -- or a call to a dedicated function like get_prediction(symbol).
            -- The get_prediction function is assumed to handle caching.
            prediction = get_prediction(symbol) -- See get_prediction_pseudocode.md

            -- Create a dictionary to hold the combined information.
            stock_info = NEW DICTIONARY

            stock_info["symbol"] = symbol
            stock_info["name"] = stock_details["name"] IF stock_details IS NOT NULL ELSE "N/A"

            -- TEST get_watchlist_stock_with_no_prediction
            -- BEHAVIOR: Should correctly handle a stock on the watchlist that has no available prediction.
            -- SETUP:
            --   1. Mock the watchlist DB query to return ['GOOG'].
            --   2. Mock get_prediction('GOOG') to return NULL or an empty dictionary.
            -- ACTION: Call the function.
            -- ASSERT: The list item for 'GOOG' has 'signal' and 'confidence' as NULL or default values.
            IF prediction IS NOT NULL AND prediction IS NOT EMPTY THEN
                stock_info["signal"] = prediction["signal"]
                stock_info["confidence"] = prediction["confidence"]
            ELSE
                stock_info["signal"] = NULL
                stock_info["confidence"] = NULL
            END IF

            -- Add the combined stock information to our list.
            ADD stock_info TO full_watchlist
        END FOR

        RETURN full_watchlist

    CATCH DatabaseException as e
        LOG "Database error in get_watchlist for user_id {user_id}: {e.message}"
        RETURN [] -- Return an empty list on database failure.
    CATCH Exception as e
        LOG "An unexpected error occurred in get_watchlist for user_id {user_id}: {e.message}"
        RETURN [] -- Return an empty list on any other failure.
    END TRY
END FUNCTION
```

## TDD Anchors Summary

-   **`test_get_watchlist_success`**: Verifies the happy path where a user has a watchlist and all stocks have predictions.
-   **`test_get_watchlist_for_empty_watchlist`**: Checks that an empty list is returned for a user with an empty watchlist.
-   **`test_get_watchlist_stock_with_no_prediction`**: Ensures the system gracefully handles cases where a watchlist stock lacks a prediction, returning null/default values instead of failing.
-   **`test_get_watchlist_db_error_on_connect`**: Confirms that the function is resilient to database connection failures and returns an empty list.