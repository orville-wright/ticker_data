# Pseudocode: `PredictionModel.prepare_data`

This document outlines the detailed, language-agnostic pseudocode for the `prepare_data` method of the `PredictionModel` class. This revised version accepts a pre-fitted scaler to prevent lookahead bias. The method is now a pure transformation function, responsible for scaling data with the provided scaler and creating sequences suitable for an LSTM model.

## 1. Method Signature

```
FUNCTION prepare_data(self, data, scaler) -> TUPLE(Array, Array)
```

-   **CLASS:** `PredictionModel`
-   **METHOD:** `prepare_data`
-   **INPUT:**
    -   `data` (DataFrame) -- A DataFrame containing time-series features.
    -   `scaler` (Object) -- A pre-fitted scaler object (e.g., `MinMaxScaler`).
-   **OUTPUT:** A tuple containing two NumPy arrays-- `X` (input sequences) and `y` (target sequences).

## 2. Pre-conditions

-   The `scaler` object passed as a parameter must already be fitted (e.g., on a training dataset).
-   `self.sequence_length` (integer) must be defined.
-   `self.prediction_horizon` (integer) must be defined.
-   The input `data` DataFrame must contain all necessary features in a consistent column order that matches the data the scaler was fitted on.

## 3. Pseudocode

```
BEGIN FUNCTION prepare_data(self, data, scaler)

  -- TDD ANCHOR: Test for insufficient data length
  -- BEHAVIOR: Should return empty arrays if the DataFrame is too small to form a single sequence.
  -- SETUP: Set sequence_length=60, prediction_horizon=5. Pass in a dummy scaler.
  -- ACTION: Call prepare_data with a DataFrame containing 64 rows.
  -- ASSERT: The function returns two empty arrays.
  IF number of rows in data < self.sequence_length + self.prediction_horizon THEN
    LOG "Warning-- Data length is insufficient to create any sequences."
    RETURN (empty_numpy_array, empty_numpy_array)
  END IF

  -- Step 1: Scale the feature data using the provided pre-fitted scaler.
  -- This method ONLY transforms the data; it does NOT fit the scaler.
  LOG "Transforming data using the provided scaler..."
  scaled_data = scaler.transform(data)

  -- TDD ANCHOR: Test that data is correctly scaled
  -- BEHAVIOR: All values in the output array should be within the scaler's range (e.g., 0 to 1).
  -- SETUP: Create a fitted scaler.
  -- ACTION: Call prepare_data with a sample DataFrame and the fitted scaler.
  -- ASSERT: Check that MIN(X) >= 0 and MAX(X) <= 1 for a MinMaxScaler.

  -- Define the column index for the target variable (e.g., 'close' price).
  -- This is a critical assumption-- we'll assume the target is the first column.
  target_column_index = 0

  -- Step 2: Initialize lists to hold the sequences
  X_sequences = new empty List
  y_sequences = new empty List

  -- Step 3: Iterate through the scaled data to create sequences
  last_possible_start_index = length of scaled_data - self.sequence_length - self.prediction_horizon
  FOR i FROM 0 TO last_possible_start_index

    -- Extract the input sequence
    input_start = i
    input_end = i + self.sequence_length
    input_sequence = scaled_data from row input_start to input_end

    -- Extract the target sequence
    target_start = input_end
    target_end = target_start + self.prediction_horizon
    target_sequence_full = scaled_data from row target_start to target_end
    
    -- Extract only the target column for the y-values
    target_values = target_sequence_full[:, target_column_index]

    -- Append the sequences to their respective lists
    APPEND input_sequence to X_sequences
    APPEND target_values to y_sequences

  END FOR

  -- Step 4: Convert the lists of sequences into NumPy arrays
  -- TDD ANCHOR: Test for correct output shapes
  -- BEHAVIOR: The returned arrays X and y should have the expected dimensions.
  -- SETUP: Use a DataFrame with 100 rows, sequence_length=60, prediction_horizon=5, and 10 features.
  -- ACTION: Call prepare_data.
  -- ASSERT: The shape of the returned X array is (100 - 60 - 5 + 1, 60, 10).
  -- ASSERT: The shape of the returned y array is (100 - 60 - 5 + 1, 5).
  X_array = CONVERT X_sequences to NumPy array
  y_array = CONVERT y_sequences to NumPy array

  -- Step 5: Return the prepared data
  RETURN (X_array, y_array)

END FUNCTION
```

## 4. Post-conditions

-   The method returns a tuple of two NumPy arrays.
-   The first array, `X`, has the shape `(num_samples, sequence_length, num_features)`.
-   The second array, `y`, has the shape `(num_samples, prediction_horizon)`.
-   `num_samples` will be `len(data) - sequence_length - prediction_horizon + 1`.
