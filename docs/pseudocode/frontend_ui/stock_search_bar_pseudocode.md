# Pseudocode: StockSearchBar Component

This document outlines the logic for the `StockSearchBar` component, which provides a user interface for searching stocks and displaying dynamic suggestions.

## 1. Component Definition

COMPONENT StockSearchBar

  ### State
    - `query`: STRING -- Stores the user's input text. Initialized to an empty string.
    - `suggestions`: LIST of DICTIONARY -- Stores the list of stock suggestions returned from the API. Each dictionary contains stock details (e.g., symbol, name). Initialized to an empty list.
    - `isLoading`: BOOLEAN -- A flag to indicate when an API call to fetch suggestions is in progress. Initialized to `FALSE`.
    - `debounceTimer`: TIMER -- A reference to a timer used for debouncing API calls. Initialized to `NULL`.

  ### Props
    - `onStockSelect`: FUNCTION -- A callback function passed from a parent component. It is invoked when a user selects a stock. It accepts one argument: the stock `symbol` (STRING).

## 2. Functions

### FUNCTION handleInputChange(event)
  - **Description:** Triggered on every keystroke in the search input field. It updates the query state and schedules the `fetchSuggestions` function to run after a short delay to prevent excessive API calls.
  - **Input:** `event` -- The input change event from the DOM, containing the new value.

  BEGIN FUNCTION handleInputChange(event)
    -- 1. Update the query state with the new value from the input field.
    SET `state.query` to `event.target.value`

    -- 2. Clear any existing debounce timer to reset the delay.
    CLEAR_TIMER(`state.debounceTimer`)

    -- 3. If the new query is empty, clear suggestions and do not proceed.
    IF `state.query` is empty THEN
      SET `state.suggestions` to `[]`
      RETURN
    END IF

    -- 4. Set a new timer to call `fetchSuggestions` after a specified delay (e.g., 300ms).
    --    This prevents firing an API request on every single keystroke.
    SET `state.debounceTimer` to NEW_TIMER(CALL `fetchSuggestions` AFTER 300 milliseconds)
  END FUNCTION

### FUNCTION fetchSuggestions()
  - **Description:** Asynchronously fetches stock suggestions from the backend API based on the current `query` state.
  - **Input:** None.

  BEGIN ASYNC FUNCTION fetchSuggestions()
    -- TEST: `fetchSuggestions` behavior for a valid query
    -- DESCRIPTION: Should set `isLoading`, call the API, and update `suggestions` on success.

    -- 1. Check if the query is too short to avoid pointless API calls.
    IF length of `state.query` < 2 THEN
      SET `state.suggestions` to `[]`
      RETURN
    END IF

    -- 2. Set loading state to true to indicate an API call is starting.
    SET `state.isLoading` to `TRUE`

    -- 3. Use a try-catch-finally block for robust API call handling.
    TRY
      -- 4. Make a GET request to the backend search endpoint.
      --    The query is passed as a URL parameter.
      LET `response` = AWAIT API_GET(`/api/stocks/search?q=${state.query}`)

      -- 5. Check if the response was successful.
      IF `response.status` is 200 THEN
        -- TEST: API success path
        -- DESCRIPTION: `suggestions` state should be populated with data from a successful API response.
        LET `data` = `response.json()`
        SET `state.suggestions` to `data`
      ELSE
        -- TEST: API error path
        -- DESCRIPTION: `suggestions` state should be cleared on API error.
        SET `state.suggestions` to `[]`
        -- Optionally, log the error or set an error state.
        LOG `Error fetching suggestions: ${response.statusText}`
      END IF
    CATCH `error`
      -- TEST: Network or exception path
      -- DESCRIPTION: `suggestions` state should be cleared if the API call throws an exception.
      SET `state.suggestions` to `[]`
      LOG `An error occurred: ${error}`
    FINALLY
      -- 6. Reset the loading state regardless of the outcome.
      SET `state.isLoading` to `FALSE`
    END TRY
  END ASYNC FUNCTION

### FUNCTION handleSelect(symbol)
  - **Description:** Triggered when a user clicks on a suggestion from the list. It invokes the parent's callback and clears the current search state.
  - **Input:** `symbol` (STRING) -- The symbol of the stock selected by the user.

  BEGIN FUNCTION handleSelect(symbol)
    -- TEST: `handleSelect` behavior
    -- DESCRIPTION: Should invoke the `onStockSelect` prop with the correct symbol and clear the local state.

    -- 1. Call the `onStockSelect` function passed in via props, providing the selected symbol.
    CALL `props.onStockSelect`(symbol)

    -- 2. Clear the query and suggestions to reset the search bar's state.
    SET `state.query` to `""`
    SET `state.suggestions` to `[]`
  END FUNCTION

## 3. TDD Anchors

-   **`TEST: StockSearchBar component renders correctly`**
    -   **BEHAVIOR:** Should render an input field without any initial suggestions.
    -   **SETUP:** Render the component with a mock `onStockSelect` function.
    -   **ACTION:** No action needed.
    -   **ASSERT:** The document should contain an input element. The list of suggestions should be empty.

-   **`TEST: Fetches and displays suggestions on user input`**
    -   **BEHAVIOR:** Should fetch and display suggestions as a user types a valid query.
    -   **SETUP:** Render the component. Mock the API GET call to `/api/stocks/search?q=APP` to return a sample list, e.g., `[{ symbol: 'AAPL', name: 'Apple Inc.' }]`.
    -   **ACTION:** Simulate a user typing "APP" into the search input. Wait for the debounce timer to elapse.
    -   **ASSERT:** The component should display a list item containing "AAPL - Apple Inc.".

-   **`TEST: Invokes onStockSelect when a suggestion is clicked`**
    -   **BEHAVIOR:** Should call the `onStockSelect` prop with the correct symbol when a user clicks a suggestion.
    -   **SETUP:** Render the component and mock the API to provide suggestions as in the previous test. Create a mock/spy for the `onStockSelect` prop.
    -   **ACTION:** Simulate a user typing "APP", then simulate a click on the "AAPL - Apple Inc." suggestion.
    -   **ASSERT:** The mock `onStockSelect` function should be called exactly once with the argument "AAPL". The suggestion list and query should be cleared after the selection.

-   **`TEST: Does not fetch for very short queries`**
    -   **BEHAVIOR:** Should not trigger an API call if the query length is less than the defined threshold (e.g., 2 characters).
    -   **SETUP:** Render the component. Create a spy on the API fetching logic.
    -   **ACTION:** Simulate a user typing "A" into the search input.
    -   **ASSERT:** The API spy should not have been called.