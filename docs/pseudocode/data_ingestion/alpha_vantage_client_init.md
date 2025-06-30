# Pseudocode: AlphaVantageClient.__init__

This document provides the detailed, language-agnostic pseudocode for the `__init__` method of the `AlphaVantageClient` class.

## 1. Method Signature

`FUNCTION __init__(api_key)`

## 2. Description

Initializes an instance of the `AlphaVantageClient`. It sets up the necessary properties for making API requests, including the user's API key and the service's base URL.

## 3. Parameters

-   `api_key` (String) -- **Required**. The unique API key provided by Alpha Vantage for authenticating requests.

## 4. Returns

-   `None`. The method is a constructor and does not return a value. It modifies the state of the new object instance.

## 5. TDD Anchors

-   `TEST_initialization_success`:
    -   **BEHAVIOR**: The client should be initialized correctly with a valid API key.
    -   **SETUP**: Provide a non-empty string as the `api_key`.
    -   **ACTION**: Create a new instance of `AlphaVantageClient`.
    -   **ASSERT**: The instance's `api_key` property matches the provided key.
    -   **ASSERT**: The instance's `base_url` property is set to "https://www.alphavantage.co/query".

-   `TEST_initialization_with_invalid_key`:
    -   **BEHAVIOR**: The constructor should raise an error if the API key is invalid (e.g., empty, null, or not a string).
    -   **SETUP**: Provide an empty string `""` as the `api_key`.
    -   **ACTION**: Attempt to create a new instance of `AlphaVantageClient`.
    -   **ASSERT**: A `ValueError` (or an equivalent invalid argument error) is raised.

## 6. Pseudocode

```plaintext
CLASS AlphaVantageClient

    -- Properties
    PROPERTY api_key AS String
    PROPERTY base_url AS String

    -- Constructor
    FUNCTION __init__(api_key):
        -- TDD Anchor: TEST_initialization_with_invalid_key
        -- Validate the input to ensure the api_key is a non-empty string.
        IF api_key IS NULL OR api_key IS NOT a String OR api_key IS an empty string THEN
            THROW ValueError with message "API key must be a non-empty string."
        END IF

        -- TDD Anchor: TEST_initialization_success
        -- Assign the validated api_key to the instance property.
        self.api_key = api_key

        -- Set the constant base URL for all Alpha Vantage API calls.
        self.base_url = "https://www.alphavantage.co/query"

        -- No return value for a constructor.
    END FUNCTION

END CLASS