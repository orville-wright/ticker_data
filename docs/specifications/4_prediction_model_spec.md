# Specification: Time-Series Prediction Model

This document provides the technical specifications for the LSTM-based time-series prediction model. This model is the core of the platform, responsible for generating the final "buy," "sell," or "hold" signal based on the processed features.

## 1. Overview

The prediction model component will be a class that encapsulates an LSTM (Long Short-Term Memory) neural network built with TensorFlow/Keras. This class will manage the model's lifecycle, including its creation, training, evaluation, and prediction. It will also handle the necessary data preparation steps, such as scaling and sequencing.

---

## 2. Prediction Model Class

### 2.1. Class: `PredictionModel`

A class for building, training, and using an LSTM model for stock trend prediction.

#### Properties

-   `model` (`tf.keras.Model`): The compiled Keras LSTM model.
-   `scaler` (`sklearn.preprocessing.MinMaxScaler`): The scaler used to normalize the feature data.
-   `sequence_length` (int): The number of time steps to look back in each input sequence (e.g., 60 days).
-   `prediction_horizon` (int): The number of time steps to predict into the future (e.g., 5 days).

#### Methods

-   `__init__(self, sequence_length: int = 60, prediction_horizon: int = 5)`
    -   **Description:** Initializes the `PredictionModel` instance, setting the sequence length and prediction horizon.
    -   **Parameters:**
        -   `sequence_length` (int): The number of past days' data to use for a single prediction.
        -   `prediction_horizon` (int): The number of future days to predict.
    -   **Returns:** `None`

-   `build_model(self, input_shape: tuple)`
    -   **Description:** Constructs the LSTM model architecture using Keras. The model will consist of multiple LSTM layers with Dropout, followed by a Dense output layer.
    -   **Parameters:**
        -   `input_shape` (tuple): The shape of the input data, which will be `(sequence_length, num_features)`.
    -   **Returns:** `None`
    -   **TDD Anchor/Pseudocode Stub:**
        ```python
        # TEST: test_build_model
        # BEHAVIOR: Should create a Keras model with the correct architecture.
        # SETUP: Initialize PredictionModel.
        # ACTION: Call build_model with a sample input shape (e.g., (60, 10)).
        # ASSERT: self.model is not None and is an instance of tf.keras.Model.
        # ASSERT: The model's input and output shapes match the expected dimensions.
        ```

-   `prepare_data(self, data: 'pd.DataFrame') -> tuple[np.ndarray, np.ndarray]`
    -   **Description:** Scales the input DataFrame and transforms it into sequences of a specified length for training or prediction.
    -   **Parameters:**
        -   `data` (pd.DataFrame): The feature-rich DataFrame from the processing pipeline.
    -   **Returns:** `tuple[np.ndarray, np.ndarray]`: A tuple containing the input sequences (X) and target sequences (y).

-   `train(self, data: 'pd.DataFrame', epochs: int = 50, batch_size: int = 32)`
    -   **Description:** Trains the LSTM model on the provided historical data. This involves preparing the data, building the model if it doesn't exist, and running the training loop. To prevent data leakage during validation, this method is also responsible for fitting the data scaler (`self.scaler`) exclusively on the training data it receives.
    -   **Parameters:**
        -   `data` (pd.DataFrame): The full historical dataset for a single stock.
        -   `epochs` (int): The number of training epochs.
        -   `batch_size` (int): The size of each training batch.
    -   **Returns:** `tf.keras.callbacks.History`: The training history object.

-   `predict(self, data: 'pd.DataFrame') -> dict`
    -   **Description:** Makes a prediction for the next `prediction_horizon` days. It takes the most recent `sequence_length` days of data, prepares it, and feeds it to the trained model. It then interprets the output to generate a "buy," "sell," or "hold" signal and a confidence score.
    -   **Parameters:**
        -   `data` (pd.DataFrame): A DataFrame containing at least `sequence_length` days of the most recent data.
    -   **Returns:** `dict`: A dictionary containing the signal, confidence score, and the predicted price movement. Example: `{'signal': 'BUY', 'confidence': 0.82, 'predicted_price_change_percent': 5.2}`.
    -   **TDD Anchor/Pseudocode Stub:**
        ```python
        # TEST: test_predict_signal
        # BEHAVIOR: Should return a valid signal dictionary.
        # SETUP: Load a pre-trained model and scaler into a PredictionModel instance.
        # INPUT: A sample DataFrame with recent data.
        # ACTION: Call predict.
        # ASSERT: The returned dictionary contains 'signal', 'confidence' keys.
        # ASSERT: The 'signal' is one of 'BUY', 'SELL', 'HOLD'.
        # ASSERT: The 'confidence' is a float between 0 and 1.
        ```

-   `save_model(self, file_path: str)`
    -   **Description:** Saves the trained Keras model and the associated scaler to a specified location.
    -   **Parameters:**
        -   `file_path` (str): The base path to save the model and scaler files (e.g., 'models/AAPL').
    -   **Returns:** `None`

-   `load_model(self, file_path: str)`
    -   **Description:** Loads a previously trained model and its scaler from a file.
    -   **Parameters:**
        -   `file_path` (str): The base path where the model and scaler are stored.
    -   **Returns:** `None`
