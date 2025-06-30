# Pseudocode: remove_from_watchlist

## 1. Description

This document provides detailed, language-agnostic pseudocode for the `remove_from_watchlist` function. This function is responsible for removing a specified stock from an authenticated user's watchlist.

## 2. Function Definition

```
FUNCTION remove_from_watchlist(user_id: integer, symbol: string) -> boolean
```

### **Parameters:**

*   `user_id` (integer): The unique identifier for the authenticated user.
*   `symbol` (string): The stock ticker symbol to be removed from the watchlist.

### **Returns:**

*   (boolean): `True` if the stock was successfully removed, `False` otherwise.

## 3. SPARC Pseudocode

```
BEGIN FUNCTION remove_from_watchlist(user_id, symbol)

  // TEST: test_remove_from_watchlist_not_found
  // BEHAVIOR: Should return False if the symbol is not in the user's watchlist.
  // SETUP: Mock the database to ensure the user's watchlist does not contain the specified symbol.
  // ACTION: Call the function with a user_id and a symbol not in their list.
  // ASSERT: The function returns False. The API should respond with a 404 Not Found status.

  // Step 1: Access the database or data store.
  // This could be a direct database connection or an ORM session.
  DB_CONNECTION = acquire_database_connection()

  TRY
    // Step 2: Find the specific watchlist item to remove.
    // Query the 'watchlist' table (or equivalent collection) for an entry
    // that matches both the user_id and the stock symbol.
    watchlist_item = DB_CONNECTION.query(
      "SELECT * FROM watchlists WHERE user_id = :user_id AND symbol = :symbol",
      user_id=user_id,
      symbol=symbol
    )

    // Step 3: Check if the item exists.
    IF watchlist_item IS NULL THEN
      // The stock is not in the user's watchlist.
      LOG "Attempted to remove non-existent symbol '{symbol}' from watchlist for user_id {user_id}."
      RETURN False
    END IF

    // TEST: test_remove_from_watchlist_success
    // BEHAVIOR: Should return True if the symbol is successfully removed.
    // SETUP: Mock the database to include the specified symbol in the user's watchlist.
    // ACTION: Call the function with the user_id and the symbol to remove.
    // ASSERT: The function returns True. Verify the item was deleted from the mock database. The API should respond with a 204 No Content status.

    // Step 4: If the item exists, remove it from the database.
    DB_CONNECTION.execute(
      "DELETE FROM watchlists WHERE user_id = :user_id AND symbol = :symbol",
      user_id=user_id,
      symbol=symbol
    )

    // Step 5: Commit the transaction to make the deletion permanent.
    DB_CONNECTION.commit()

    LOG "Successfully removed symbol '{symbol}' from watchlist for user_id {user_id}."

    // Step 6: Return True to indicate success.
    RETURN True

  CATCH DatabaseError as e
    // Step 7: Handle potential database errors.
    LOG "Database error during watchlist removal for user {user_id}: {e.message}"
    // Rollback any partial changes if the transaction failed.
    DB_CONNECTION.rollback()
    RETURN False

  FINALLY
    // Step 8: Always release the database connection.
    release_database_connection(DB_CONNECTION)
  END TRY

END FUNCTION
```

## 4. TDD Anchors Summary

*   **test_remove_from_watchlist_not_found**: Verifies that the function correctly handles cases where the stock symbol is not present in the user's watchlist, returning `False`.
*   **test_remove_from_watchlist_success**: Ensures the function successfully removes an existing stock from the watchlist and returns `True`.
