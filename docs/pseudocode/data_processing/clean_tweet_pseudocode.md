# Pseudocode: TweetProcessor.clean_tweet

This document provides detailed, language-agnostic pseudocode for the `clean_tweet` static method of the `TweetProcessor` class. This method is responsible for cleaning raw tweet text to prepare it for further processing and analysis.

## 1. Method Signature

```
FUNCTION clean_tweet(text AS STRING) RETURNS STRING
```

## 2. Pre-conditions

-   The input `text` is a raw string, potentially containing URLs, mentions, hashtags, and mixed-case characters.

## 3. Post-conditions

-   The output is a cleaned string, with specific elements removed or transformed, and all characters in lowercase.

## 4. TDD Anchors

These anchors guide the Test-Driven Development process for this function.

---
-   **TEST:** `test_clean_tweet_happy_path`
    -   **BEHAVIOR:** Should remove URLs, user mentions, and the hashtag symbol, then convert the entire string to lowercase, based on the provided specification example.
    -   **INPUT:** `"Check out $AAPL news! @user1 https://example.com #StockMarket"`
    -   **EXPECTED_OUTPUT:** `"check out $aapl news! stockmarket"`
    -   **ASSERT:** The function's output exactly matches the `EXPECTED_OUTPUT` string.

-   **TEST:** `test_clean_tweet_with_no_special_elements`
    -   **BEHAVIOR:** Should correctly convert a simple string to lowercase.
    -   **INPUT:** `"A simple tweet about stocks"`
    -   **EXPECTED_OUTPUT:** `"a simple tweet about stocks"`
    -   **ASSERT:** The output is the lowercase version of the input.

-   **TEST:** `test_clean_tweet_with_multiple_hashtags_and_mentions`
    -   **BEHAVIOR:** Should handle multiple occurrences of each element to be cleaned.
    -   **INPUT:** `"@person1 says #stocks are #awesome. @person2 agrees. See http://a.co"`
    -   **EXPECTED_OUTPUT:** `"says stocks are awesome. agrees. see"`
    -   **ASSERT:** All mentions, hashtags, and the URL are correctly removed/transformed.

-   **TEST:** `test_clean_tweet_with_empty_string`
    -   **BEHAVIOR:** Should return an empty string if the input is empty.
    -   **INPUT:** `""`
    -   **EXPECTED_OUTPUT:** `""`
    -   **ASSERT:** The function handles empty input gracefully.

-   **TEST:** `test_clean_tweet_retains_dollar_sign_for_tickers`
    -   **BEHAVIOR:** Should not remove the dollar sign `$` typically used for stock tickers.
    -   **INPUT:** `"$TSLA to the moon! #tesla"`
    -   **EXPECTED_OUTPUT:** `"$tsla to the moon! tesla"`
    -   **ASSERT:** The `$` is preserved in the output string.

---

## 5. Pseudocode Logic

```pseudocode
FUNCTION clean_tweet(text AS STRING) RETURNS STRING:

  // TEST: test_clean_tweet_with_empty_string
  IF text is empty or null THEN
    RETURN ""
  END IF

  // Initialize a variable to hold the processed text.
  // This allows for sequential application of cleaning steps.
  processed_text = text

  // 1. Remove URLs
  // Use a regular expression to find and replace all occurrences of
  // web URLs (starting with http://, https://, or www.) with an empty string.
  // TEST: test_clean_tweet_happy_path, test_clean_tweet_with_multiple_hashtags_and_mentions
  processed_text = REGEX_REPLACE(processed_text, "http\S+--www\.\S+", "")

  // 2. Remove User Mentions
  // Use a regular expression to find and replace all user mentions
  // (e.g., "@username") with an empty string.
  // TEST: test_clean_tweet_happy_path, test_clean_tweet_with_multiple_hashtags_and_mentions
  processed_text = REGEX_REPLACE(processed_text, "@\w+", "")

  // 3. Handle Hashtags
  // Use a regular expression to find hashtags (#) and replace them
  // with just the text part of the hashtag. For example, "#StockMarket" becomes "StockMarket".
  // This preserves the keyword from the hashtag.
  // TEST: test_clean_tweet_happy_path, test_clean_tweet_with_multiple_hashtags_and_mentions
  processed_text = REGEX_REPLACE(processed_text, "#(\w+)", "\1") // \1 refers to the captured group (the word)

  // 4. Convert to Lowercase
  // Convert the entire string to lowercase to ensure uniformity.
  // TEST: test_clean_tweet_happy_path, test_clean_tweet_with_no_special_elements
  processed_text = TO_LOWERCASE(processed_text)

  // 5. Clean up extra whitespace
  // Multiple spaces might result from the removal of elements.
  // Replace multiple consecutive spaces with a single space and trim leading/trailing whitespace.
  processed_text = REGEX_REPLACE(processed_text, "\s+", " ")
  processed_text = TRIM_WHITESPACE(processed_text)

  // Return the fully cleaned text
  RETURN processed_text

END FUNCTION
```

## 6. Notes on "Special Characters"

The specification mentions removing "special characters". However, the provided example (`"check out $aapl news! stockmarket"`) explicitly retains the `$` and `!` characters. The pseudocode logic above aligns with this example by targeting only specific patterns (URLs, mentions, hashtags) rather than performing a blanket removal of all non-alphanumeric characters. This approach is less destructive and preserves potentially important symbols like the dollar sign for stock tickers.