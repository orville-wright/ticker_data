# Pseudocode: PredictionModel.__init__

This document outlines the detailed, language-agnostic pseudocode for the `__init__` method of the `PredictionModel` class.

## 1. Method: `__init__`

Initializes a new instance of the `PredictionModel`, setting up its core configuration parameters for time-series prediction.

---

### 1.1. SPARC Description

**Specification:**
- The constructor initializes the `PredictionModel` with a `sequence_length` and a `prediction_horizon`.

**Pseudocode:**
- The pseudocode will define a `CONSTRUCTOR` that accepts `sequence_length` and `prediction_horizon` as arguments.
- It will assign these arguments to instance variables.
- It will also initialize other instance properties like `model` and `scaler` to a default `NULL` state.

**Architecture:**
- This method is the entry point for creating a `PredictionModel` object. The `sequence_length` and `prediction_horizon` are fundamental to how data is prepared and how the model is structured. The `model` and `scaler` are initialized as `NULL` because they are stateful objects that will be created and configured in subsequent steps, such as `build_model` or `load_model`.

**Refinement:**
- The pseudocode includes explicit TDD anchors to ensure that instances are created with the correct default and custom values.

**Completion:**
- The final pseudocode is a clear blueprint for implementing the constructor in any object-oriented language.

---

### 1.2. Pseudocode

```plaintext
CLASS PredictionModel

    -- Attributes
    PROPERTY model -- The machine learning model object.
    PROPERTY scaler -- The data scaler object.
    PROPERTY sequence_length -- Integer: The number of past time steps for prediction.
    PROPERTY prediction_horizon -- Integer: The number of future time steps to predict.

    -- CONSTRUCTOR: Initializes the PredictionModel instance.
    --
    -- INPUT:
    --   sequence_length (Integer, default: 60): The number of past days' data to use for a single prediction.
    --   prediction_horizon (Integer, default: 5): The number of future days to predict.
    --
    -- OUTPUT:
    --   None: The constructor initializes the object state.
    --
    -- TDD ANCHOR: TEST behavior: Should initialize with default values.
    -- SETUP: Create an instance of PredictionModel without arguments.
    -- ACTION: Inspect the instance's properties.
    -- ASSERT: this.sequence_length equals 60.
    -- ASSERT: this.prediction_horizon equals 5.
    -- ASSERT: this.model is NULL.
    -- ASSERT: this.scaler is NULL.
    --
    -- TDD ANCHOR: TEST behavior: Should initialize with custom values.
    -- SETUP: Create an instance of PredictionModel with sequence_length=120 and prediction_horizon=10.
    -- ACTION: Inspect the instance's properties.
    -- ASSERT: this.sequence_length equals 120.
    -- ASSERT: this.prediction_horizon equals 10.
    --
    CONSTRUCTOR(sequence_length = 60, prediction_horizon = 5)
        -- Assign the configuration parameters to instance properties.
        this.sequence_length = sequence_length
        this.prediction_horizon = prediction_horizon

        -- Initialize stateful properties to NULL. They will be populated
        -- by other methods like build_model, train, or load_model.
        this.model = NULL
        this.scaler = NULL
    END CONSTRUCTOR

END CLASS
```

---

### 1.3. TDD Anchors and Test Cases

1.  **Test Case: Initialization with Default Values**
    -   **Behavior:** The model should initialize with the default `sequence_length` of 60 and `prediction_horizon` of 5.
    -   **Setup:** Instantiate `PredictionModel` with no parameters.
    -   **Action:** Check the values of `sequence_length`, `prediction_horizon`, `model`, and `scaler`.
    -   **Assert:**
        -   `sequence_length` is 60.
        -   `prediction_horizon` is 5.
        -   `model` is `NULL`.
        -   `scaler` is `NULL`.

2.  **Test Case: Initialization with Custom Values**
    -   **Behavior:** The model should accept and correctly assign custom values for its parameters.
    -   **Setup:** Instantiate `PredictionModel` with `sequence_length=120` and `prediction_horizon=10`.
    -   **Action:** Check the values of `sequence_length` and `prediction_horizon`.
    -   **Assert:**
        -   `sequence_length` is 120.
        -   `prediction_horizon` is 10.
