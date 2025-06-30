# Pseudocode: PredictionModel.build_model

## Description

This document outlines the pseudocode for the `build_model` method in the `PredictionModel` class. This method constructs a multi-layer Long Short-Term Memory (LSTM) neural network model for time-series prediction using a sequential model API, like the one found in Keras.

---

## SPARC Pseudocode

```
CLASS PredictionModel

  METHOD build_model(self, input_shape)
    --
    -- Builds and compiles the LSTM model architecture.
    --
    -- INPUT:
    --   input_shape (tuple) -- The shape of the input data for the model,
    --                          typically (sequence_length, num_features).
    --
    -- OUTPUT: None
    --
    -- BEHAVIOR:
    --   - Creates a sequential model.
    --   - Adds multiple LSTM layers with Dropout for regularization.
    --   - The final LSTM layer does not return sequences.
    --   - Adds a Dense output layer with units equal to the prediction_horizon.
    --   - Compiles the model with an optimizer and loss function.
    --   - Assigns the compiled model to self.model.
    --

    -- TDD Anchor: Test that the model is created with the correct architecture.
    -- TEST: test_build_model
    -- BEHAVIOR: Should create a Keras model with the correct architecture.
    -- SETUP: Initialize PredictionModel.
    -- ACTION: Call build_model with a sample input shape (e.g., (60, 10)).
    -- ASSERT: self.model is not None and is an instance of a valid Model object.
    -- ASSERT: The model's input shape matches the provided input_shape.
    -- ASSERT: The model's output shape matches (None, self.prediction_horizon).

    // 1. Initialize a sequential model builder
    model_builder = INITIALIZE_SEQUENTIAL_MODEL()

    // 2. Add the first LSTM layer
    // This layer needs to know the input shape and should return sequences
    // because the next layer is also an LSTM layer.
    model_builder.ADD_LAYER(
      LSTM(units=50, return_sequences=True, input_shape=input_shape)
    )
    // Add a dropout layer to prevent overfitting
    model_builder.ADD_LAYER(Dropout(rate=0.2))

    // 3. Add the second LSTM layer
    // This layer also returns sequences for the subsequent LSTM layer.
    model_builder.ADD_LAYER(
      LSTM(units=50, return_sequences=True)
    )
    model_builder.ADD_LAYER(Dropout(rate=0.2))

    // 4. Add the third LSTM layer
    // This is the final LSTM layer, so it should not return sequences.
    model_builder.ADD_LAYER(
      LSTM(units=50, return_sequences=False)
    )
    model_builder.ADD_LAYER(Dropout(rate=0.2))

    // 5. Add the output layer
    // A Dense layer that outputs a value for each day in the prediction horizon.
    model_builder.ADD_LAYER(
      Dense(units=self.prediction_horizon)
    )

    // 6. Compile the model
    // Specify the optimizer and the loss function. Mean Squared Error is common
    // for regression problems like price prediction.
    model_builder.COMPILE(optimizer='adam', loss='mean_squared_error')

    // 7. Assign the constructed and compiled model to the instance property
    self.model = model_builder.GET_MODEL()

    // 8. Log the model summary for verification
    LOG(self.model.summary())

  END_METHOD

END_CLASS