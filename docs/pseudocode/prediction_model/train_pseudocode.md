# Pseudocode: PredictionModel.train()

This document outlines the detailed logic for the `train` method within the `PredictionModel` class. This revision corrects a lookahead bias by ensuring the data scaler is fitted *only* on the training subset of the data.

## 1. Method Overview

**Method:** `train(self, data: 'pd.DataFrame', validation_split_ratio: float = 0.2, epochs: int = 50, batch_size: int = 32)`

**Description:** Trains the LSTM model on historical data. It splits the data into training and validation sets, initializes and fits a scaler on the training data *only*, prepares both datasets into sequences using the fitted scaler, builds the model if needed, and runs the training loop using the separate validation set.

---

## 2. Pseudocode

```plaintext
FUNCTION train(data, validation_split_ratio, epochs, batch_size):
  INPUT:
    - data: DataFrame containing the full historical feature set for a stock.
    - validation_split_ratio: Float between 0 and 1, the proportion of data to reserve for validation.
    - epochs: Integer, the number of training iterations.
    - batch_size: Integer, the number of samples per gradient update.
  OUTPUT:
    - history: A Keras History object containing training metrics.

  -- TEST: test_train_end_to_end
  -- BEHAVIOR: Should successfully train the model and return a history object without data leakage.
  -- SETUP: Initialize PredictionModel. Provide a sample DataFrame.
  -- ACTION: Call train() with the data.
  -- ASSERT: The returned history object is not None and contains validation metrics.
  -- ASSERT: self.model is trained (weights are updated).
  -- ASSERT: self.scaler is fitted.

  LOG "Starting model training process..."

  // Step 1: Split data into training and validation sets
  LOG "Splitting data into training and validation sets..."
  split_index = floor(length of data * (1 - validation_split_ratio))
  train_data = data from start to split_index
  validation_data = data from split_index to end

  -- TEST: test_data_split
  -- BEHAVIOR: Should split the data correctly into training and validation sets.
  -- ACTION: Call train() on a dataframe of 100 rows with validation_split_ratio=0.2.
  -- ASSERT: The train_data has 80 rows.
  -- ASSERT: The validation_data has 20 rows.

  // Step 2: Initialize and fit the scaler ONLY on the training data.
  LOG "Initializing and fitting the data scaler on the training data..."
  self.scaler = new MinMaxScaler()
  CALL self.scaler.fit(train_data)
  LOG "Scaler fitted successfully."

  -- TEST: test_scaler_is_fitted_only_on_train_data
  -- BEHAVIOR: The scaler must only learn the distribution of the training data.
  -- SETUP: Initialize PredictionModel. Provide a sample DataFrame.
  -- ACTION: Call train().
  -- ASSERT: The scaler's `fit` method was called exclusively with the `train_data` subset.

  // Step 3: Prepare training and validation data into sequences using the fitted scaler.
  LOG "Preparing training data into sequences..."
  (X_train, y_train) = CALL self.prepare_data(train_data, self.scaler)

  LOG "Preparing validation data into sequences..."
  (X_val, y_val) = CALL self.prepare_data(validation_data, self.scaler)

  -- TEST: test_prepare_data_is_called_for_both_sets
  -- BEHAVIOR: Ensure prepare_data is called for both train and validation sets with the same scaler.
  -- SETUP: Mock `prepare_data` on a PredictionModel instance.
  -- ACTION: Call train().
  -- ASSERT: The mocked `prepare_data` was called twice.
  -- ASSERT: The first call was with train_data, the second with validation_data. Both with the fitted scaler.

  // Step 4: Build the model if it has not been built yet.
  IF self.model IS NULL:
    LOG "Model not found. Building a new model..."
    input_shape = (X_train.shape[1], X_train.shape[2])
    CALL self.build_model(input_shape)
    LOG "Model built successfully."
  ELSE:
    LOG "Using existing model for training."
  END IF

  // Step 5: Execute the training loop with the explicit validation set.
  LOG "Starting Keras model fitting..."
  history = CALL self.model.fit(
    X_train,
    y_train,
    epochs=epochs,
    batch_size=batch_size,
    validation_data=(X_val, y_val),
    verbose=1
  )
  -- TEST: test_model_fit_uses_explicit_validation_set
  -- BEHAVIOR: The Keras `fit` method must be called with the prepared validation data, not a split ratio.
  -- SETUP: Initialize PredictionModel, build a mock model.
  -- ACTION: Call train().
  -- ASSERT: The mock model's `fit` method was called with `validation_data=(X_val, y_val)`.

  LOG "Model training completed."

  RETURN history
END FUNCTION
```

---

## 3. TDD Anchors

A summary of the tests that should be created to validate the functionality of the `train` method:

| Test Name                                  | Behavior Description                                                              |
| ------------------------------------------ | --------------------------------------------------------------------------------- |
| `test_train_end_to_end`                    | Should successfully train the model and return a history object.                  |
| `test_data_split`                          | Should split the data correctly into training and validation sets.                |
| `test_scaler_is_fitted_only_on_train_data` | The scaler must be fitted exclusively on the training data subset.                |
| `test_prepare_data_is_called_for_both_sets`| Ensures `prepare_data` is called for both sets with the same fitted scaler.       |
| `test_model_fit_uses_explicit_validation_set`| The Keras `fit` method must be called with the prepared `validation_data` tuple. |
