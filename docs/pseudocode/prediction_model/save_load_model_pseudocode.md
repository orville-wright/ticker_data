# Pseudocode: PredictionModel Save and Load

This document outlines the detailed, language-agnostic pseudocode for the `save_model` and `load_model` methods of the `PredictionModel` class.

---

## 1. `save_model` Method

### 1.1. Method Signature

`FUNCTION save_model(file_path AS STRING)`

### 1.2. Description

Saves the trained Keras model and the associated scaler object to a specified file path. The method will create two files: one for the model and one for the scaler.

### 1.3. TDD Anchors

-   **TEST `test_save_model_creates_files`**:
    -   **BEHAVIOR**: Should create both a model file and a scaler file at the specified path.
    -   **SETUP**: Create a `PredictionModel` instance, assign a mock Keras model to `self.model` and a mock scaler object to `self.scaler`.
    -   **ACTION**: Call `save_model` with a temporary file path.
    -   **ASSERT**: Check that a model file (e.g., `temp_path_model.h5`) exists.
    -   **ASSERT**: Check that a scaler file (e.g., `temp_path_scaler.pkl`) exists.

-   **TEST `test_save_model_no_model_error`**:
    -   **BEHAVIOR**: Should raise an error if `self.model` is null or not set.
    -   **SETUP**: Create a `PredictionModel` instance without a model.
    -   **ACTION**: Call `save_model`.
    -   **ASSERT**: An `IllegalStateException` or similar error is raised, indicating the model is not available to save.

-   **TEST `test_save_model_creates_directory`**:
    -   **BEHAVIOR**: Should create the destination directory if it does not exist.
    -   **SETUP**: Create a `PredictionModel` with a mock model and scaler.
    -   **ACTION**: Call `save_model` with a path that includes a non-existent directory.
    -   **ASSERT**: Verify that the directory has been created.

### 1.4. Pseudocode

```plaintext
FUNCTION save_model(file_path AS STRING)
    -- TEST BEHAVIOR: Guard clause for unsaved model
    IF self.model IS NULL
        THROW new IllegalStateException("Model has not been built or trained. Cannot save.")
    END IF

    -- TEST BEHAVIOR: Guard clause for missing scaler
    IF self.scaler IS NULL
        THROW new IllegalStateException("Scaler has not been fitted. Cannot save.")
    END IF

    -- Define file paths for the model and the scaler
    model_file = file_path + "_model.h5"  -- or another standard model format
    scaler_file = file_path + "_scaler.pkl" -- or another standard serialization format

    -- TEST BEHAVIOR: Ensure directory exists
    TRY
        -- Get the directory part of the file path
        directory = GET_DIRECTORY_FROM_PATH(file_path)
        -- Create the directory and any parent directories if they don't exist
        CREATE_DIRECTORY(directory, recursive=TRUE)
    CATCH FileIOException as e
        LOG "Error creating directory for model: " + e.message
        THROW e
    END TRY

    -- Save the neural network model
    TRY
        -- Use a library-specific function to save the model architecture and weights
        self.model.save(model_file)
        LOG "Model saved successfully to: " + model_file
    CATCH IOException as e
        LOG "Error saving Keras model: " + e.message
        THROW e
    END TRY

    -- Save the scaler object
    TRY
        -- Use a serialization library (e.g., pickle, joblib) to save the scaler
        SERIALIZE_OBJECT_TO_FILE(self.scaler, scaler_file)
        LOG "Scaler saved successfully to: " + scaler_file
    CATCH IOException as e
        LOG "Error saving scaler object: " + e.message
        THROW e
    END TRY

END FUNCTION
```

---

## 2. `load_model` Method

### 2.1. Method Signature

`FUNCTION load_model(file_path AS STRING)`

### 2.2. Description

Loads a trained model and its corresponding scaler from a specified file path.

### 2.3. TDD Anchors

-   **TEST `test_load_model_populates_properties`**:
    -   **BEHAVIOR**: Should correctly load the model and scaler into `self.model` and `self.scaler`.
    -   **SETUP**: Save a mock model and scaler using `save_model`.
    -   **ACTION**: Create a new `PredictionModel` instance and call `load_model` with the path from the setup.
    -   **ASSERT**: `self.model` is not null and is a valid Keras model instance.
    -   **ASSERT**: `self.scaler` is not null and is a valid scaler instance.

-   **TEST `test_load_model_file_not_found`**:
    -   **BEHAVIOR**: Should raise a `FileNotFoundError` if the model or scaler file does not exist.
    -   **SETUP**: Create a `PredictionModel` instance.
    -   **ACTION**: Call `load_model` with a path to non-existent files.
    -   **ASSERT**: A `FileNotFoundError` or similar exception is raised.

### 2.4. Pseudocode

```plaintext
FUNCTION load_model(file_path AS STRING)
    -- Define file paths for the model and the scaler
    model_file = file_path + "_model.h5"
    scaler_file = file_path + "_scaler.pkl"

    -- TEST BEHAVIOR: Check for model file existence
    IF FILE_EXISTS(model_file) IS FALSE
        THROW new FileNotFoundException("Model file not found at: " + model_file)
    END IF

    -- TEST BEHAVIOR: Check for scaler file existence
    IF FILE_EXISTS(scaler_file) IS FALSE
        THROW new FileNotFoundException("Scaler file not found at: " + scaler_file)
    END IF

    -- Load the neural network model
    TRY
        -- Use a library-specific function to load a model from a file
        self.model = LOAD_KERAS_MODEL(model_file)
        LOG "Model loaded successfully from: " + model_file
    CATCH IOException as e
        LOG "Error loading Keras model: " + e.message
        THROW e
    END TRY

    -- Load the scaler object
    TRY
        -- Use a deserialization library to load the scaler object
        self.scaler = DESERIALIZE_OBJECT_FROM_FILE(scaler_file)
        LOG "Scaler loaded successfully from: " + scaler_file
    CATCH IOException as e
        LOG "Error loading scaler object: " + e.message
        THROW e
    END TRY

END FUNCTION