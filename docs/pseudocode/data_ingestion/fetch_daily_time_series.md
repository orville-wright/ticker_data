# Pseudocode: AlphaVantageClient.fetch_daily_time_series

## 1. Description

This document provides detailed, language-agnostic pseudocode for the `fetch_daily_time_series` method of the `AlphaVantageClient` class. This method fetches daily stock time-series data from the Alpha Vantage API, implementing a robust retry mechanism with exponential backoff to handle rate limiting and transient network errors.

## 2. Constants

-   `MAX_RETRIES`: INTEGER, set to 3. The maximum number of times to retry the API call upon failure.
-   `INITIAL_DELAY`: INTEGER, set to 1 (second). The initial delay for the exponential backoff strategy.

## 3. Method Signature

`FUNCTION fetch_daily_time_series(client_instance, symbol, output_size)`

### **Inputs:**

-   `client_instance`: OBJECT. The instance of the AlphaVantageClient, containing `api_key` and `base_url`.
-   `symbol`: STRING. The stock ticker symbol (e.g., "AAPL").
-   `output_size`: STRING. The data output size ('compact' or 'full'). Defaults to 'compact'.

### **Output:**

-   `DICTIONARY`: A dictionary containing the time-series data on success, or an empty dictionary on failure after all retries.

## 4. Pseudocode

```pseudocode
FUNCTION fetch_daily_time_series(client_instance, symbol, output_size DEFAULT 'compact')

    -- TDD Anchor: TEST behavior for constructing a valid API request URL
    -- BEHAVIOR: The URL should correctly combine the base URL, function, symbol, output size, and API key.
    -- ASSERT: The generated URL matches the expected format.
    LET params = CREATE_DICTIONARY({
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": output_size,
        "apikey": client_instance.api_key
    })

    LET request_url = CONSTRUCT_URL(client_instance.base_url, params)

    LET attempts = 0
    LET delay = INITIAL_DELAY

    WHILE attempts < MAX_RETRIES DO
        -- TDD Anchor: TEST behavior for making an HTTP GET request.
        -- ACTION: Make a mock HTTP GET call to request_url.
        TRY
            LET response = HTTP_GET(request_url)

            -- TDD Anchor: TEST behavior for handling a successful response (200 OK).
            -- MOCK: HTTP response with status 200 and valid JSON data.
            IF response.status_code IS 200 THEN
                LET data = PARSE_JSON(response.body)

                -- Alpha Vantage can return a 200 OK with an error message in the JSON body
                -- TDD Anchor: TEST behavior for handling API-level error messages in a successful response.
                -- MOCK: HTTP response with status 200 and JSON body containing an "Error Message" key.
                IF "Error Message" IN data THEN
                    LOG_ERROR("API returned an error for symbol: " + symbol + ". Message: " + data["Error Message"])
                    RETURN EMPTY_DICTIONARY
                END IF

                -- TDD Anchor: TEST behavior for handling API-level rate limit notes in a successful response.
                -- MOCK: HTTP response with status 200 and JSON body containing a "Note" key about rate limiting.
                IF "Note" IN data AND "call frequency" IN data["Note"] THEN
                    -- This is a rate limit warning, treat it like a 429 to trigger backoff.
                    LOG_WARNING("Rate limit warning received for symbol: " + symbol + ". Retrying...")
                    -- Fall through to the backoff logic below by simulating a rate-limit condition
                    -- This avoids duplicating the backoff code. We can force the next check to fail.
                    -- Or more simply, continue to the next iteration with a delay.
                ELSE
                    LOG_INFO("Successfully fetched data for symbol: " + symbol)
                    RETURN data
                END IF

            -- TDD Anchor: TEST behavior for handling rate limit errors (e.g., 429 Too Many Requests).
            -- MOCK: HTTP response with status 429 on the first call, then 200 on the second.
            ELSE IF response.status_code IS 429 OR ("Note" IN data AND "call frequency" IN data["Note"]) THEN
                 LOG_WARNING("Rate limit hit for symbol: " + symbol + ". Retrying in " + delay + " seconds...")
                 -- The retry logic is handled by the loop's increment and sleep steps.

            -- TDD Anchor: TEST behavior for handling other HTTP errors (e.g., 404 Not Found, 500 Server Error).
            -- MOCK: HTTP response with status 500.
            ELSE
                LOG_ERROR("HTTP error for symbol: " + symbol + ". Status: " + response.status_code)
                -- Break the loop as this is likely a non-transient error
                BREAK
            END IF

        CATCH NetworkException as e
            -- TDD Anchor: TEST behavior for handling network exceptions.
            -- MOCK: HTTP client to raise a network-related exception (e.g., timeout, connection error).
            LOG_ERROR("Network error for symbol: " + symbol + ". Attempt " + (attempts + 1) + ". Error: " + e.message)
        END TRY


        -- Exponential backoff logic
        SLEEP(delay)
        delay = delay * 2
        attempts = attempts + 1

    END WHILE

    -- TDD Anchor: TEST behavior for failure after exhausting all retries.
    -- MOCK: HTTP response to consistently be 429 or raise an error for MAX_RETRIES times.
    -- ASSERT: The function logs a final failure message and returns an empty dictionary.
    LOG_ERROR("Failed to fetch data for symbol: " + symbol + " after " + MAX_RETRIES + " attempts.")
    RETURN EMPTY_DICTIONARY

END FUNCTION
```

## 5. TDD Anchor Summary

-   **URL Construction**: Verifies the API request URL is created correctly.
-   **HTTP Request**: Ensures the HTTP GET request is made.
-   **Success Case (200 OK)**: Handles a standard successful API response.
-   **API Error in Success Response**: Handles cases where the API returns status 200 but the payload contains an error message (e.g., invalid symbol).
-   **API Rate Limit Note in Success Response**: Handles cases where the API returns status 200 but the payload contains a rate limit warning note.
-   **Rate Limit Case (429)**: Manages retries with exponential backoff when a rate limit status code is received.
-   **Other HTTP Errors**: Gracefully handles other non-successful HTTP status codes (e.g., 404, 500).
-   **Network Exception**: Catches and logs network-level errors during the request.
-   **Retry Failure**: Confirms that the function returns an empty dictionary after all retry attempts are exhausted.