# Pseudocode: `PredictionModel.predict`

This document outlines the detailed, language-agnostic pseudocode for the `predict` method of the `PredictionModel` class.

## 1. Method Signature

**FUNCTION** `predict(self, data)`

-   **INPUT:**
    -   `data` (DataFrame): A DataFrame containing the most recent historical data for a stock. It must contain at least `self.sequence_length` records and all features used for training.
-   **OUTPUT:**
    -   `Dictionary`: A dictionary containing the prediction signal, confidence, and percentage price change.
    -   Example: `{'signal': 'BUY', 'confidence': 0.82, 'predicted_price_change_percent': 5.2}`

## 2. Constants

-   `BUY_THRESHOLD` (Float): The minimum percentage increase to trigger a "BUY" signal. Default: `2.0`.
-   `SELL_THRESHOLD` (Float): The minimum percentage decrease (as a negative number) to trigger a "SELL" signal. Default: `-2.0`.
-   `CONFIDENCE_SCALING_FACTOR` (Float): A value used to scale the predicted change into a confidence score. A 10% change could represent maximum confidence. Default: `10.0`.

## 3. Pseudocode Logic

```plaintext
FUNCTION predict(self, data):
    -- TDD Anchor: test_predict_signal_and_confidence
    -- BEHAVIOR: Should return a valid dictionary with 'signal', 'confidence', and 'predicted_price_change_percent'.
    -- SETUP: A pre-trained model and its corresponding feature and target scalers are loaded into the PredictionModel instance.
    -- INPUT: A DataFrame `data` with a number of rows >= self.sequence_length.
    -- ACTION: Call `self.predict(data)`.
    -- ASSERT: The returned dictionary contains the keys 'signal', 'confidence', and 'predicted_price_change_percent'.
    -- ASSERT: The 'signal' value is one of 'BUY', 'SELL', or 'HOLD'.
    -- ASSERT: The 'confidence' value is a float between 0.0 and 1.0.
    -- ASSERT: The 'predicted_price_change_percent' is a float.

    -- TDD Anchor: test_predict_with_insufficient_data
    -- BEHAVIOR: Should raise an error if the input data is too short.
    -- INPUT: A DataFrame `data` with a number of rows < self.sequence_length.
    -- ACTION: Call `self.predict(data)`.
    -- ASSERT: A ValueError is raised with a descriptive message.

    -- 1. Pre-computation Checks
    IF self.model IS NULL OR self.feature_scaler IS NULL OR self.target_scaler IS NULL:
        RAISE StateError("Model, feature_scaler, and target_scaler must be loaded or trained before making predictions.")
    END IF

    IF number of rows in data < self.sequence_length:
        RAISE ValueError("Input data must contain at least 'sequence_length' records.")
    END IF

    -- 2. Data Preparation
    -- Isolate the most recent sequence of data
    recent_data = last `self.sequence_length` rows of data

    -- Store the last actual price to calculate the percentage change later
    last_actual_price = recent_data.last_row['close_price']

    -- Scale the feature data using the pre-fitted feature scaler
    scaled_data = self.feature_scaler.transform(recent_data)

    -- Reshape the data to the format expected by the LSTM model: (1, sequence_length, num_features)
    prediction_input = reshape(scaled_data, (1, self.sequence_length, number_of_features_in_scaled_data))

    -- 3. Model Prediction
    -- Get the raw, scaled prediction from the model
    scaled_prediction_output = self.model.predict(prediction_input) -- Shape: (1, prediction_horizon)

    -- 4. Inverse Transform the Prediction
    -- The model outputs a scaled prediction for the target variable.
    -- We use the dedicated target_scaler to inverse transform this value back to its original price scale.
    -- The prediction output (shape: 1, horizon) is reshaped to (horizon, 1) for the scaler.
    reshaped_prediction = reshape(scaled_prediction_output, (self.prediction_horizon, 1))

    -- Inverse transform the reshaped prediction to get the unscaled price
    unscaled_prediction_array = self.target_scaler.inverse_transform(reshaped_prediction)

    -- Extract the unscaled predicted prices by flattening the array
    predicted_prices = flatten(unscaled_prediction_array)

    -- 5. Interpret the Result
    -- The final predicted price is the last one in the horizon
    final_predicted_price = last element of predicted_prices

    -- Calculate the percentage change from the last known price
    predicted_price_change_percent = ((final_predicted_price - last_actual_price) / last_actual_price) * 100

    -- 6. Generate Signal and Confidence
    signal = "HOLD"
    IF predicted_price_change_percent > BUY_THRESHOLD:
        signal = "BUY"
    ELSE IF predicted_price_change_percent < SELL_THRESHOLD:
        signal = "SELL"
    END IF

    -- Calculate confidence based on the magnitude of the predicted change
    -- This maps the absolute percentage change to a score between 0.0 and 1.0.
    absolute_change = ABS(predicted_price_change_percent)
    confidence = MIN(absolute_change / CONFIDENCE_SCALING_FACTOR, 1.0)

    -- 7. Construct and Return the Result
    result = {
        "signal": signal,
        "confidence": confidence,
        "predicted_price_change_percent": predicted_price_change_percent
    }

    RETURN result
END FUNCTION