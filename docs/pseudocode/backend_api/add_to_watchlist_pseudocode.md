# Pseudocode: add_to_watchlist

**Function:** `add_to_watchlist(user_id: int, symbol: str) -> bool`

**Description:** This function adds a specified stock symbol to a given user's watchlist in the database. It performs checks to ensure the user and stock are valid and that the stock is not already on the user's watchlist before insertion.

---

### **1. Main Function Logic**

```pseudocode
FUNCTION add_to_watchlist(user_id, symbol)
  -- TEST: Test function with valid user_id and new symbol
  -- TEST: Test function with an invalid user_id
  -- TEST: Test function with a symbol that is already in the watchlist
  -- TEST: Test function with an invalid or non-existent stock symbol
  -- TEST: Test function with null or empty symbol
  -- TEST: Test database transaction failure during insertion

  -- 1.1. Input Validation
  IF user_id is not a positive integer OR symbol is null or empty string THEN
    LOG "Invalid input: user_id or symbol is invalid."
    RETURN FALSE
  END IF

  -- 1.2. Normalize the stock symbol
  normalized_symbol = CONVERT_TO_UPPERCASE(TRIM(symbol))

  -- 1.3. Begin database transaction for atomic operation
  BEGIN TRANSACTION

  TRY
    -- 1.4. Verify the user exists
    -- TDD Anchor: MOCK database call to check for user existence
    user_exists = CHECK_IF_USER_EXISTS_IN_DB(user_id)
    IF NOT user_exists THEN
      LOG "User with id {user_id} not found."
      ROLLBACK TRANSACTION
      RETURN FALSE
    END IF

    -- 1.5. Verify the stock symbol is valid (e.g., exists in our stocks table)
    -- TDD Anchor: MOCK database call to check for stock symbol validity
    stock_exists = CHECK_IF_STOCK_EXISTS_IN_DB(normalized_symbol)
    IF NOT stock_exists THEN
      LOG "Stock symbol {normalized_symbol} not found."
      ROLLBACK TRANSACTION
      RETURN FALSE
    END IF

    -- 1.6. Check if the stock is already in the user's watchlist
    -- TDD Anchor: MOCK database call to check for existing watchlist item
    is_in_watchlist = CHECK_IF_IN_WATCHLIST(user_id, normalized_symbol)
    IF is_in_watchlist THEN
      LOG "Stock {normalized_symbol} is already in watchlist for user {user_id}."
      ROLLBACK TRANSACTION
      RETURN FALSE
    END IF

    -- 1.7. Add the stock to the user's watchlist
    -- TDD Anchor: MOCK database insertion call
    insertion_successful = INSERT_INTO_WATCHLIST_DB(user_id, normalized_symbol)
    IF NOT insertion_successful THEN
      LOG "Failed to add stock to watchlist due to a database error."
      ROLLBACK TRANSACTION
      RETURN FALSE
    END IF

    -- 1.8. Commit the transaction if all steps succeeded
    COMMIT TRANSACTION
    LOG "Successfully added {normalized_symbol} to watchlist for user {user_id}."
    RETURN TRUE

  CATCH DatabaseException as e
    -- 1.9. Handle any unexpected database errors
    LOG "Database error during add_to_watchlist: {e.message}"
    ROLLBACK TRANSACTION
    RETURN FALSE
  END TRY

END FUNCTION
```

### **2. Helper Functions (Conceptual)**

These functions represent interactions with the database.

```pseudocode
FUNCTION CHECK_IF_USER_EXISTS_IN_DB(user_id)
  -- Connect to the database
  -- Query the 'users' table for the given user_id
  -- RETURN TRUE if a record is found, otherwise FALSE
END FUNCTION

FUNCTION CHECK_IF_STOCK_EXISTS_IN_DB(symbol)
  -- Connect to the database
  -- Query the 'stocks' table for the given symbol
  -- RETURN TRUE if a record is found, otherwise FALSE
END FUNCTION

FUNCTION CHECK_IF_IN_WATCHLIST(user_id, symbol)
  -- Connect to the database
  -- Query the 'watchlist' table for a record matching user_id and symbol
  -- RETURN TRUE if a record is found, otherwise FALSE
END FUNCTION

FUNCTION INSERT_INTO_WATCHLIST_DB(user_id, symbol)
  -- Connect to the database
  -- Execute an INSERT statement into the 'watchlist' table with user_id and symbol
  -- RETURN TRUE if the insertion was successful (e.g., 1 row affected), otherwise FALSE
END FUNCTION
```

### **3. TDD Anchors**

-   **`test_add_new_stock_successfully`**:
    -   Inputs: `user_id = 1`, `symbol = "GOOG"`
    -   Mocks: `CHECK_IF_USER_EXISTS_IN_DB` returns `TRUE`, `CHECK_IF_STOCK_EXISTS_IN_DB` returns `TRUE`, `CHECK_IF_IN_WATCHLIST` returns `FALSE`, `INSERT_INTO_WATCHLIST_DB` returns `TRUE`.
    -   Expected Output: `TRUE`.
-   **`test_add_stock_for_invalid_user`**:
    -   Inputs: `user_id = 999`, `symbol = "AAPL"`
    -   Mocks: `CHECK_IF_USER_EXISTS_IN_DB` returns `FALSE`.
    -   Expected Output: `FALSE`.
-   **`test_add_invalid_stock_symbol`**:
    -   Inputs: `user_id = 1`, `symbol = "INVALID"`
    -   Mocks: `CHECK_IF_USER_EXISTS_IN_DB` returns `TRUE`, `CHECK_IF_STOCK_EXISTS_IN_DB` returns `FALSE`.
    -   Expected Output: `FALSE`.
-   **`test_add_existing_stock_to_watchlist`**:
    -   Inputs: `user_id = 1`, `symbol = "MSFT"`
    -   Mocks: `CHECK_IF_USER_EXISTS_IN_DB` returns `TRUE`, `CHECK_IF_STOCK_EXISTS_IN_DB` returns `TRUE`, `CHECK_IF_IN_WATCHLIST` returns `TRUE`.
    -   Expected Output: `FALSE`.
-   **`test_add_stock_with_database_insertion_failure`**:
    -   Inputs: `user_id = 1`, `symbol = "TSLA"`
    -   Mocks: `CHECK_IF_USER_EXISTS_IN_DB` returns `TRUE`, `CHECK_IF_STOCK_EXISTS_IN_DB` returns `TRUE`, `CHECK_IF_IN_WATCHLIST` returns `FALSE`, `INSERT_INTO_WATCHLIST_DB` returns `FALSE`.
    -   Expected Output: `FALSE`.
-   **`test_add_stock_with_null_input`**:
    -   Inputs: `user_id = 1`, `symbol = null`
    -   Expected Output: `FALSE`.