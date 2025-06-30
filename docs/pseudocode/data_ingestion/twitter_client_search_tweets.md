# Pseudocode: TwitterClient.search_tweets

## 1. Description

This document provides detailed, language-agnostic pseudocode for the `search_tweets` method of the `TwitterClient` class. This method searches for recent tweets matching a query using the Twitter API v2. It implements a robust retry mechanism with exponential backoff to handle rate limiting (HTTP 429) and transient network errors, ensuring data pipeline resilience.

## 2. Constants

-   `MAX_RETRIES`: INTEGER, set to 3. The maximum number of times to retry the API call upon failure.
-   `INITIAL_DELAY`: INTEGER, set to 1 (second). The initial delay for the exponential backoff strategy.
-   `TWITTER_API_ENDPOINT`: STRING, the base URL for the Twitter search endpoint (e.g., "https://api.twitter.com/2/tweets/search/recent").

## 3. Method Signature

`FUNCTION search_tweets(client_instance, query, max_results)`

### **Inputs:**

-   `client_instance`: OBJECT. The instance of the TwitterClient, containing the `bearer_token`.
-   `query`: STRING. The search query string.
-   `max_results`: INTEGER. The number of tweets to return. Defaults to 100.

### **Output:**

-   `LIST[DICTIONARY]`: A list of tweet objects on success, or an empty list on failure after all retries.

## 4. Pseudocode

```pseudocode
FUNCTION search_tweets(client_instance, query, max_results DEFAULT 100)

    -- TDD Anchor: TEST behavior for constructing a valid API request
    -- BEHAVIOR: The headers and parameters should be correctly formatted for the Twitter API.
    -- ASSERT: The generated headers contain the correct Bearer token and params match expected format.
    LET headers = CREATE_DICTIONARY({
        "Authorization": "Bearer " + client_instance.bearer_token
    })

    LET params = CREATE_DICTIONARY({
        "query": query,
        "max_results": max_results
    })

    LET attempts = 0
    LET delay = INITIAL_DELAY

    WHILE attempts < MAX_RETRIES DO
        -- TDD Anchor: TEST behavior for making an HTTP GET request.
        -- ACTION: Make a mock HTTP GET call to the Twitter API endpoint with correct headers and params.
        TRY
            LET response = HTTP_GET(TWITTER_API_ENDPOINT, headers=headers, params=params)

            -- TDD Anchor: TEST behavior for handling a successful response (200 OK).
            -- MOCK: HTTP response with status 200 and valid JSON data containing a 'data' key.
            IF response.status_code IS 200 THEN
                LET response_data = PARSE_JSON(response.body)
                LOG_INFO("Successfully fetched tweets for query: " + query)
                -- The actual tweets are usually in a 'data' field in the Twitter API v2 response
                RETURN response_data.get("data", EMPTY_LIST)

            -- TDD Anchor: TEST behavior for handling rate limit errors (429 Too Many Requests).
            -- MOCK: HTTP response with status 429 on the first call, then 200 on the second.
            ELSE IF response.status_code IS 429 THEN
                 LOG_WARNING("Rate limit hit for query: " + query + ". Retrying in " + delay + " seconds...")
                 -- The retry logic is handled by the loop's increment and sleep steps.

            -- TDD Anchor: TEST behavior for handling other HTTP errors (e.g., 400 Bad Request, 500 Server Error).
            -- MOCK: HTTP response with status 400 or 500.
            ELSE
                LET error_message = PARSE_JSON(response.body)
                LOG_ERROR("HTTP error for query: " + query + ". Status: " + response.status_code + ". Details: " + error_message)
                -- Break the loop as this is likely a non-transient error (e.g., bad query)
                BREAK
            END IF

        CATCH NetworkException as e
            -- TDD Anchor: TEST behavior for handling network exceptions.
            -- MOCK: HTTP client to raise a network-related exception (e.g., timeout, connection error).
            LOG_ERROR("Network error for query: " + query + ". Attempt " + (attempts + 1) + ". Error: " + e.message)
        END TRY


        -- Exponential backoff logic
        SLEEP(delay)
        delay = delay * 2
        attempts = attempts + 1

    END WHILE

    -- TDD Anchor: TEST behavior for failure after exhausting all retries.
    -- MOCK: HTTP response to consistently be 429 or raise an error for MAX_RETRIES times.
    -- ASSERT: The function logs a final failure message and returns an empty list.
    LOG_ERROR("Failed to fetch tweets for query: " + query + " after " + MAX_RETRIES + " attempts.")
    RETURN EMPTY_LIST

END FUNCTION
```

## 5. TDD Anchor Summary

-   **Request Construction**: Verifies the API request headers and parameters are created correctly.
-   **HTTP Request**: Ensures the HTTP GET request is made to the correct endpoint.
-   **Success Case (200 OK)**: Handles a standard successful API response and returns a list of tweets.
-   **Rate Limit Case (429)**: Manages retries with exponential backoff when a rate limit status code is received.
-   **Other HTTP Errors**: Gracefully handles other non-successful HTTP status codes (e.g., 400, 500) and stops retrying.
-   **Network Exception**: Catches and logs network-level errors during the request.
-   **Retry Failure**: Confirms that the function returns an empty list after all retry attempts are exhausted.