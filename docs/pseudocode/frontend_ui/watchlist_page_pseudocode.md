# Pseudocode: WatchlistPage View

This document outlines the detailed logic for the `WatchlistPage` view, which is responsible for displaying and managing the user's stock watchlist.

## Component: WatchlistPage

**Purpose:** To provide a dashboard view of the user's entire watchlist, allowing them to see the latest prediction signals and remove items.

**State:**
-   `watchlist` (LIST of DICTIONARIES): Stores the collection of stock objects fetched from the backend. Each object contains details like symbol, name, signal, etc. Initial state is an empty list.
-   `isLoading` (BOOLEAN): Tracks the loading state for the initial page load. Initial state is `true`.
-   `removingItems` (LIST of STRINGS): Stores the symbols of items currently being processed for removal to show item-specific loading indicators. Initial state is an empty list.
-   `error` (STRING or NULL): Stores any error message if an API call fails. Initial state is `null`.

---

### FUNCTION `fetchWatchlist()`

**Trigger:** Called automatically when the `WatchlistPage` component is first mounted or loaded.

**Purpose:** To fetch the user's complete watchlist from the backend API and update the component's state.

```pseudocode
FUNCTION fetchWatchlist()
    // TEST: Behavior for successful watchlist fetch
    // DESCRIPTION: Should fetch data from the API and populate the watchlist state.

    // Set loading state to indicate data fetching is in progress
    SET isLoading = TRUE
    SET error = NULL

    // Define the API endpoint for fetching the watchlist
    CONSTANT API_ENDPOINT = "/api/watchlist"

    // Use a TRY-CATCH block for robust error handling during the API call
    TRY
        // Make an asynchronous GET request to the API
        // AWAIT: Pauses execution until the API call completes
        RESPONSE = AWAIT HTTP.GET(API_ENDPOINT)

        // TEST: Behavior for successful API response (HTTP 200)
        // DESCRIPTION: Should update the watchlist state with the fetched data.
        IF RESPONSE.status IS 200 THEN
            // Parse the JSON data from the response body
            DATA = RESPONSE.json()
            // Update the component's state with the fetched watchlist data
            SET watchlist = DATA
        ELSE
            // TEST: Behavior for non-200 API response (e.g., 404, 500)
            // DESCRIPTION: Should set an appropriate error message.
            SET error = "Failed to fetch watchlist. Server returned status: " + RESPONSE.status
            // Ensure the watchlist is empty if the fetch fails
            SET watchlist = []
        END IF

    CATCH exception
        // TEST: Behavior for network error or API failure
        // DESCRIPTION: Should capture the exception and set an error message.
        SET error = "An error occurred while fetching the watchlist: " + exception.message
        SET watchlist = []

    FINALLY
        // Whether the API call succeeded or failed, turn off the loading indicator
        SET isLoading = FALSE
    END TRY

END FUNCTION
```

---

### FUNCTION `handleRemoveItem(symbol)`

**Trigger:** Called when a user initiates a removal action from a child component (e.g., clicking a "Remove" button in a `WatchlistRow`).

**Purpose:** To remove a specific stock from the user's watchlist via an API call and update the local state only after successful confirmation from the server.

**Input:**
-   `symbol` (STRING): The stock symbol to be removed from the watchlist.

```pseudocode
FUNCTION handleRemoveItem(symbol)
    // TEST: Behavior for removing an item from the watchlist
    // DESCRIPTION: Should call the DELETE API and remove the item from the local state upon success.

    // Input validation
    IF symbol IS NULL OR symbol IS EMPTY THEN
        PRINT "Error: Symbol cannot be empty for removal."
        RETURN
    END IF

    // Set loading state for the specific item to provide user feedback (e.g., show a spinner)
    ADD symbol TO removingItems

    // Define the dynamic API endpoint for deleting a specific stock
    CONSTANT API_ENDPOINT = "/api/watchlist/" + symbol

    // Use a TRY-CATCH-FINALLY block for robust API call handling
    TRY
        // Make an asynchronous DELETE request to the API
        RESPONSE = AWAIT HTTP.DELETE(API_ENDPOINT)

        // TEST: Behavior for successful API deletion (HTTP 204 or 200)
        // DESCRIPTION: Should remove the item from the local `watchlist` state.
        IF RESPONSE.status IS 204 (No Content) OR RESPONSE.status IS 200 THEN
            // On success, update the local state to remove the item
            NEW_WATCHLIST = FILTER watchlist WHERE item.symbol IS NOT equal to symbol
            SET watchlist = NEW_WATCHLIST
            // Clear any previous error messages
            SET error = NULL
        ELSE
            // TEST: Behavior for failed API deletion
            // DESCRIPTION: Should display an error message and not alter the watchlist.
            SET error = "Failed to remove " + symbol + ". Server returned status: " + RESPONSE.status
        END IF

    CATCH exception
        // TEST: Behavior for network error during deletion
        // DESCRIPTION: Should display an error message.
        SET error = "An error occurred while removing " + symbol + ": " + exception.message

    FINALLY
        // Whether the API call succeeded or failed, remove the item from the loading state
        REMOVE symbol FROM removingItems
    END TRY

END FUNCTION