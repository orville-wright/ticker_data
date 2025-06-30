# WatchlistButton Component Pseudocode

This document outlines the pseudocode for the `WatchlistButton` component, which allows users to add or remove a stock from their watchlist.

## Component-Level State and Properties

-   **`symbol`** (String)
    -   **Description**: The stock symbol to be managed (e.g., "AAPL", "GOOG").
    -   **Passed as**: Property from a parent component.

-   **`isOnWatchlist`** (Boolean)
    -   **Description**: A stateful property indicating if the stock is currently in the user's watchlist. This controls the button's appearance and behavior.
    -   **Managed by**: The component's internal state, updated after API calls.

## Functions

---

### 1. `handleClick()`

This function serves as the primary event handler for the button's click event. It acts as a router, delegating the action to the appropriate function based on the current `isOnWatchlist` state.

**Pseudocode:**

```
FUNCTION handleClick()
  // TDD Anchor: TEST handleClick calls addToWatchlist when isOnWatchlist is false.
  IF this.isOnWatchlist IS false THEN
    CALL addToWatchlist()
  ELSE
    // TDD Anchor: TEST handleClick calls removeFromWatchlist when isOnWatchlist is true.
    CALL removeFromWatchlist()
  END IF
END FUNCTION
```

---

### 2. `addToWatchlist()`

This function handles the logic for adding a stock to the user's watchlist. It involves making an API call and updating the component's state upon success.

**Pseudocode:**

```
FUNCTION addToWatchlist()
  // TDD Anchor: TEST addToWatchlist successfully adds a stock and updates the UI state.
  // TDD Anchor: TEST addToWatchlist handles API errors gracefully without crashing.

  BEGIN TRY
    // Announce the action to provide user feedback, e.g., by disabling the button.
    SET component_state to 'loading'

    // TDD Anchor: TEST that the correct API endpoint and method are called.
    // API call to add the stock. The body contains the symbol.
    API_RESPONSE = HTTP_POST("/api/watchlist", BODY: { "symbol": this.symbol })

    // TDD Anchor: TEST that a successful API response updates the component state.
    IF API_RESPONSE.status IS 201 (Created) or 200 (OK) THEN
      // Update the component's state to reflect the change.
      SET this.isOnWatchlist = true
      // Optional: Display a success message to the user.
      DISPLAY_NOTIFICATION("Added " + this.symbol + " to watchlist.", type: "success")
    ELSE
      // Handle API errors (e.g., 400 Bad Request, 500 Server Error).
      // TDD Anchor: TEST that API error responses are handled and reported to the user.
      LOG "API Error in addToWatchlist: " + API_RESPONSE.body.message
      DISPLAY_NOTIFICATION("Error: Could not add " + this.symbol, type: "error")
    END IF

  CATCH network_error
    // Handle exceptions like network failures.
    // TDD Anchor: TEST that network errors are caught and reported.
    LOG "Network Exception in addToWatchlist: " + network_error.message
    DISPLAY_NOTIFICATION("Network error. Please try again.", type: "error")

  FINALLY
    // Re-enable the button or remove the loading state.
    SET component_state to 'idle'
  END TRY
END FUNCTION
```

---

### 3. `removeFromWatchlist()`

This function handles the logic for removing a stock from the user's watchlist. It involves a `DELETE` request to the API and updates the state on success.

**Pseudocode:**

```
FUNCTION removeFromWatchlist()
  // TDD Anchor: TEST removeFromWatchlist successfully removes a stock and updates UI state.
  // TDD Anchor: TEST removeFromWatchlist handles API errors gracefully.

  BEGIN TRY
    // Announce the action to provide user feedback.
    SET component_state to 'loading'

    // TDD Anchor: TEST that the correct API endpoint, method, and symbol are used.
    // API call to remove the stock. The symbol is part of the URL path.
    API_RESPONSE = HTTP_DELETE("/api/watchlist/" + this.symbol)

    // TDD Anchor: TEST that a successful API response updates the component state.
    IF API_RESPONSE.status IS 200 (OK) or 204 (No Content) THEN
      // Update the component's state to reflect the change.
      SET this.isOnWatchlist = false
      // Optional: Display a success message.
      DISPLAY_NOTIFICATION("Removed " + this.symbol + " from watchlist.", type: "success")
    ELSE
      // Handle API errors.
      // TDD Anchor: TEST that API error responses are handled and reported to the user.
      LOG "API Error in removeFromWatchlist: " + API_RESPONSE.body.message
      DISPLAY_NOTIFICATION("Error: Could not remove " + this.symbol, type: "error")
    END IF

  CATCH network_error
    // Handle exceptions like network failures.
    // TDD Anchor: TEST that network errors are caught and reported.
    LOG "Network Exception in removeFromWatchlist: " + network_error.message
    DISPLAY_NOTIFICATION("Network error. Please try again.", type: "error")

  FINALLY
    // Re-enable the button or remove the loading state.
    SET component_state to 'idle'
  END TRY
END FUNCTION