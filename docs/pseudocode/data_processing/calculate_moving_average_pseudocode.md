# Pseudocode: FeatureEngineer.calculate_moving_average

This document provides detailed, language-agnostic pseudocode for the `calculate_moving_average` method of the `FeatureEngineer` class. It serves as a blueprint for implementation and testing.

## 1. Method Signature

```
STATIC METHOD calculate_moving_average(data, window)
```

## 2. Description

Calculates the Simple Moving Average (SMA) for the 'close' price column within a given dataset. The SMA is a technical indicator that shows the average price over a specified period.

## 3. Parameters

-   **`data`**: A data structure (e.g., DataFrame) containing historical time-series data. It MUST include a 'close' column with numerical price values.
-   **`window`**: An INTEGER representing the size of the rolling window for the moving average calculation (e.g., 20 for a 20-day SMA).

## 4. Returns

-   A data structure (e.g., Series) containing the calculated SMA values. The length of this structure will be the same as the input `data`, with initial values being null or NaN until the first full window is available.

## 5. Logic

```pseudocode
FUNCTION calculate_moving_average(data, window)
    -- TDD Anchor: TEST behavior for missing 'close' column
    -- BEHAVIOR: Should raise a specific error if the 'close' column does not exist in the input data.
    IF 'close' column does NOT exist in data THEN
        THROW InvalidInputError("Input data must contain a 'close' column.")
    END IF

    -- TDD Anchor: TEST behavior for invalid window size
    -- BEHAVIOR: Should raise an error if the window size is less than 1.
    IF window < 1 THEN
        THROW InvalidInputError("Window size must be a positive integer.")
    END IF

    -- TDD Anchor: TEST behavior for window larger than data
    -- BEHAVIOR: Should return a series of null/NaN values if the window is larger than the dataset length.
    IF window > LENGTH(data) THEN
        -- Create a new series of the same length as data, filled with nulls
        LET empty_sma_series = CREATE_SERIES(length=LENGTH(data), fill_value=NULL)
        RETURN empty_sma_series
    END IF

    -- Select the 'close' price column from the data
    LET close_prices = data['close']

    -- TDD Anchor: TEST behavior for happy path calculation
    -- BEHAVIOR: Should correctly calculate the SMA for a given window.
    -- SETUP: Create sample data with known 'close' prices.
    -- INPUT: data = [10, 12, 11, 13, 15], window = 3
    -- EXPECTED_OUTPUT: [NULL, NULL, 11.0, 12.0, 13.0]
    -- ASSERT: The calculated series matches the expected output.

    -- Apply a rolling window function to the close prices
    -- For each window, calculate the mean
    LET moving_average_series = close_prices.rolling(window_size=window).mean()

    -- Return the resulting series
    RETURN moving_average_series
END FUNCTION
```

## 6. TDD Anchors Summary

A comprehensive test suite for this method should include the following checks:

1.  **`test_calculate_sma_happy_path`**: Verifies that the SMA is calculated correctly for a standard input DataFrame and a valid window size.
2.  **`test_missing_close_column_raises_error`**: Ensures the method fails gracefully with a descriptive error if the input `data` lacks the required 'close' column.
3.  **`test_window_larger_than_data_returns_nulls`**: Checks that if the `window` size exceeds the number of data points, the method returns a Series of the correct length filled entirely with null/NaN values.
4.  **`test_invalid_window_size_raises_error`**: Confirms that a non-positive integer for the `window` parameter raises an appropriate error.
5.  **`test_data_with_nan_values`**: Verifies that the calculation handles `NaN` values within the 'close' price series correctly, propagating NaNs as expected.
