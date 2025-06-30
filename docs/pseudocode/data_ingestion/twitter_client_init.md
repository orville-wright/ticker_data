# Pseudocode: TwitterClient.__init__

## SPARC Pseudocode Design

This document provides a detailed, language-agnostic pseudocode blueprint for the `TwitterClient` constructor. It adheres to SPARC design principles, ensuring clarity, testability, and a solid foundation for implementation.

---

### **Class: TwitterClient**

**Purpose:** To encapsulate all interactions with the Twitter/X API v2.

#### **Properties**

-   `bearer_token` (String): Stores the API bearer token for authentication.
-   `base_url` (String): The constant base URL for the Twitter API's recent search endpoint.

---

### **CONSTRUCTOR: `__init__(bearer_token)`**

**Description:** Initializes a new instance of the `TwitterClient`.

**Inputs:**
-   `bearer_token` (String): The bearer token required for authenticating with the Twitter/X API v2.

**Outputs:**
-   `None`

**Processing Logic:**

1.  **Input Validation**
    -   `TEST: test_constructor_with_invalid_token`
    -   `BEHAVIOR: Should raise an error if the bearer_token is null, empty, or not a string.`
    -   `IF` the provided `bearer_token` is `NULL` or an empty string `THEN`
        -   `THROW` a `ValueError` with the message "Bearer token cannot be null or empty."
    -   `END IF`

2.  **Property Assignment**
    -   `TEST: test_constructor_assigns_properties_correctly`
    -   `BEHAVIOR: Should correctly assign the bearer_token and set the default base_url.`
    -   Assign the input `bearer_token` to the instance property `this.bearer_token`.
    -   Assign the constant string "https://api.twitter.com/2/tweets/search/recent" to the instance property `this.base_url`.

3.  **Return**
    -   This is a constructor, so it does not explicitly return a value. The initialized object is the result.

---

### **TDD Anchors Summary**

A summary of the tests required to validate the `__init__` method's behavior:

| Test Case Name                               | Behavior Description                                                        |
| -------------------------------------------- | --------------------------------------------------------------------------- |
| `test_constructor_assigns_properties_correctly` | Verifies that `bearer_token` and `base_url` are set correctly on the instance. |
| `test_constructor_with_invalid_token`        | Ensures the constructor raises a specific error for null or empty tokens. |
