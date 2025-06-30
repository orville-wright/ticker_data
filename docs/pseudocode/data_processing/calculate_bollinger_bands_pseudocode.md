# Pseudocode for `calculate_bollinger_bands`

## FeatureEngineer.calculate_bollinger_bands

This document outlines the pseudocode for the `calculate_bollinger_bands` static method.

### Method Signature

```
STATIC METHOD calculate_bollinger_bands(data, window)
```

### **Inputs**

-   `data`: A data structure (e.g., DataFrame) containing time-series data with a 'close' price column.
-   `window`: An integer representing the period for the moving average and standard deviation calculation (default is 20).

### **Outputs**

-   A tuple containing two series:
    -   `upper_band`: A series representing the upper Bollinger Band.
    -   `lower_band`: A series representing the lower Bollinger Band.

### **Pre-conditions**

-   The input `data` must contain a numeric column named 'close'.
-   The 'close' column must not contain null or non-numeric values where calculations are performed.
-   The `window` parameter must be a positive integer.

### **Post-conditions**

-   The method returns two data series of the same length as the input 'close' price series.
-   The initial `window - 1` values in the returned series will be null/NaN, as they don't have enough preceding data for calculation.

---

### **Pseudocode Logic**

```plaintext
FUNCTION calculate_bollinger_bands(data, window = 20):
    // TDD Anchor: TEST behavior for valid inputs
    // TDD Anchor: TEST that the function returns a tuple of two series

    // 1. Validate inputs
    // TDD Anchor: TEST behavior for missing 'close' column in data
    IF 'close' column NOT IN data:
        THROW InvalidInputError with message "Input data must contain a 'close' column."
    END IF

    // TDD Anchor: TEST behavior for non-positive window value
    IF window <= 0:
        THROW InvalidInputError with message "Window must be a positive integer."
    END IF

    // 2. Calculate the Middle Band (Simple Moving Average)
    // The middle band is the moving average of the 'close' price over the specified window.
    // TDD Anchor: TEST middle band calculation against a known dataset
    middle_band = calculate_rolling_mean(data['close'], window)

    // 3. Calculate the Standard Deviation
    // The standard deviation is calculated for the 'close' price over the same window.
    // TDD Anchor: TEST standard deviation calculation against a known dataset
    std_dev = calculate_rolling_std_dev(data['close'], window)

    // 4. Calculate the Upper and Lower Bands
    // The upper band is the middle band plus two times the standard deviation.
    // The lower band is the middle band minus two times the standard deviation.
    // TDD Anchor: TEST upper band calculation logic
    upper_band = middle_band + (2 * std_dev)

    // TDD Anchor: TEST lower band calculation logic
    lower_band = middle_band - (2 * std_dev)

    // TDD Anchor: TEST that the first (window - 1) elements are null/NaN
    // TDD Anchor: TEST that the length of output series matches input series length

    // 5. Return the bands
    RETURN (upper_band, lower_band)

END FUNCTION
```

### TDD Anchors Summary

-   **Input Validation:**
    -   `TEST behavior for valid inputs`: Ensures the function runs without errors with correct data and window size.
    -   `TEST behavior for missing 'close' column in data`: Verifies that an appropriate error is raised.
    -   `TEST behavior for non-positive window value`: Checks for correct error handling if the window is 0 or negative.
-   **Calculation Logic:**
    -   `TEST middle band calculation against a known dataset`: Validates the Simple Moving Average logic.
    -   `TEST standard deviation calculation against a known dataset`: Validates the rolling standard deviation logic.
    -   `TEST upper band calculation logic`: Confirms the upper band is correctly calculated as `SMA + 2 * StdDev`.
    -   `TEST lower band calculation logic`: Confirms the lower band is correctly calculated as `SMA - 2 * StdDev`.
-   **Output Verification:**
    -   `TEST that the function returns a tuple of two series`: Checks the output data type and structure.
    -   `TEST that the first (window - 1) elements are null/NaN`: Ensures that calculations are correctly skipped for the initial period.
    -   `TEST that the length of output series matches input series length`: Verifies the output dimension is correct.