# Pseudocode: FeatureEngineer.calculate_rsi

This document provides a detailed, language-agnostic pseudocode for the `calculate_rsi` method, adhering to SPARC design principles.

## 1. Method Signature

- **Class:** `FeatureEngineer`
- **Method:** `calculate_rsi`
- **Type:** Static Class Method
- **Inputs:**
  - `data` (DataFrame): A data structure containing historical price data, which must include a 'close' column.
  - `window` (Integer): The look-back period for the RSI calculation. Default is 14.
- **Output:** `Series`: A data series containing the calculated RSI values for each time period.

## 2. High-Level Logic

The method calculates the Relative Strength Index (RSI), a momentum oscillator that measures the speed and change of price movements. The RSI oscillates between zero and 100.

---

## 3. Step-by-Step Pseudocode

```plaintext
FUNCTION calculate_rsi(data, window = 14)

  // TDD Anchor: TEST behavior for invalid input
  // BEHAVIOR: Should raise an error or return an empty Series if 'close' column is missing.
  // INPUT: DataFrame without a 'close' column
  // EXPECTED_OUTCOME: Error raised or empty Series returned.
  IF 'close' column is NOT in data THEN
    LOG "Error: 'close' column not found in DataFrame."
    RETURN an empty Series or RAISE ValueError
  END IF

  // 1. Calculate Price Changes
  // Get the difference in price from one period to the next.
  SET delta = data['close'].difference(1)

  // 2. Separate Gains and Losses
  // Create two new series: one for gains (positive changes) and one for losses (negative changes).
  SET gain = delta.copy()
  SET loss = delta.copy()

  // For the 'gain' series, set all non-positive values to 0.
  // For the 'loss' series, take the absolute value of negative changes and set all non-negative values to 0.
  gain[gain < 0] = 0
  loss[loss > 0] = 0
  loss = loss.absolute()

  // TDD Anchor: TEST behavior for correct gain/loss separation
  // BEHAVIOR: Should correctly identify and separate positive and negative price changes.
  // INPUT: A series of price changes like [1, -2, 3, -1]
  // EXPECTED_gain: [1, 0, 3, 0]
  // EXPECTED_loss: [0, 2, 0, 1]
  // ASSERT: The generated gain and loss series match the expected outputs.

  // 3. Calculate Average Gains and Losses
  // Use an exponential moving average (EMA) for smoothing.
  // Some libraries might use a simple moving average (SMA) for the first window period.
  // We will specify the more common EMA approach.
  SET avg_gain = gain.ewm(com=window - 1, min_periods=window).mean()
  SET avg_loss = loss.ewm(com=window - 1, min_periods=window).mean()

  // 4. Calculate Relative Strength (RS)
  // RS = Average Gain / Average Loss.
  // Handle the edge case where avg_loss is zero to prevent division by zero errors.
  SET rs = avg_gain / avg_loss
  // Where avg_loss is 0, rs will be infinity, which is handled in the next step.

  // 5. Calculate the RSI
  // RSI = 100 - (100 / (1 + RS))
  SET rsi = 100.0 - (100.0 / (1.0 + rs))

  // TDD Anchor: TEST behavior for RSI calculation
  // BEHAVIOR: Should produce the correct RSI value based on a known sequence of gains and losses.
  // SETUP:
  //   - A 'close' price series that results in a predictable avg_gain and avg_loss.
  //   - For a 14-day period, if avg_gain = 10 and avg_loss = 5, then RS = 2.
  // EXPECTED_RSI: 100 - (100 / (1 + 2)) = 66.67
  // ASSERT: The calculated RSI value at the specific period matches the expected value.

  // TDD Anchor: TEST behavior for handling zero loss
  // BEHAVIOR: When average loss is zero, RSI should be 100.
  // SETUP: A sequence where there are only gains and no losses over the window.
  // EXPECTED_RSI: 100
  // ASSERT: The RSI value is 100.

  RETURN rsi

END FUNCTION
```

## 4. Summary of TDD Anchors

-   **Test for Missing Column:** Ensures the function is robust against malformed input data.
-   **Test Gain/Loss Separation:** Verifies the core logic of correctly identifying positive and negative price movements.
-   **Test RSI Calculation:** Confirms the final RSI formula is implemented correctly using a known input/output pair.
-   **Test Zero Loss Scenario:** Validates the edge case where the price only goes up, which should result in an RSI of 100.

---