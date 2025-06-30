# Pseudocode: search_stocks

## FUNCTION: search_stocks

### PURPOSE
Searches a data source of stocks for matches based on a query string, comparing against both ticker symbols and company names. This function is intended to power the `GET /api/stocks/search` endpoint.

### INPUTS
- `query` (String) -- The search term provided by the user (e.g., "AAPL", "Apple").

### OUTPUTS
- `matching_stocks` (List of Dictionaries) -- A list of stock objects that match the query. Each dictionary contains 'symbol' and 'name'. Returns an empty list if no matches are found.

### TDD ANCHORS

- **TEST: search_by_symbol_partial_match**
  - **BEHAVIOR:** Should return stocks where the query is a partial, case-insensitive match for the ticker symbol.
  - **SETUP:** Mock the stock data source with entries like `{"symbol": "AAPL", "name": "Apple Inc."}`, `{"symbol": "AAPT", "name": "AAPlus Corp."}`.
  - **ACTION:** Call `search_stocks` with `query="aap"`.
  - **ASSERT:** The returned list contains both "AAPL" and "AAPT" stock dictionaries.

- **TEST: search_by_name_partial_match**
  - **BEHAVIOR:** Should return stocks where the query is a partial, case-insensitive match for the company name.
  - **SETUP:** Mock the stock data source with entries like `{"symbol": "AAPL", "name": "Apple Inc."}`, `{"symbol": "MSFT", "name": "Microsoft Corp."}`.
  - **ACTION:** Call `search_stocks` with `query="apple"`.
  - **ASSERT:** The returned list contains the "AAPL" stock dictionary.

- **TEST: search_with_empty_query**
  - **BEHAVIOR:** Should return an empty list if the query string is empty or contains only whitespace.
  - **ACTION:** Call `search_stocks` with `query="   "`.
  - **ASSERT:** The returned list is empty.

- **TEST: search_with_no_matches**
  - **BEHAVIOR:** Should return an empty list if no stocks match the query.
  - **ACTION:** Call `search_stocks` with `query="nonexistent_stock_xyz"`.
  - **ASSERT:** The returned list is empty.

- **TEST: result_format_is_correct**
  - **BEHAVIOR:** The returned list of dictionaries must contain 'symbol' and 'name' keys.
  - **SETUP:** Mock a stock entry, e.g., `{"symbol": "GOOG", "name": "Alphabet Inc."}`.
  - **ACTION:** Call `search_stocks` with a query that matches the mock entry (e.g., "GOOG").
  - **ASSERT:** The first element in the returned list has keys 'symbol' and 'name' with the correct values.

### LOGIC

1.  **FUNCTION** `search_stocks`(**INPUT** `query`):
2.      **INITIALIZE** `matching_stocks` as an empty List.
3.
4.      //-- TDD Anchor: search_with_empty_query
5.      //-- Validate the input query string.
6.      **IF** `query` is NULL **OR** `query` trimmed of whitespace is empty:
7.          **RETURN** `matching_stocks`.
8.      **END IF**
9.
10.     **INITIALIZE** `normalized_query` = `query` converted to lowercase and trimmed of whitespace.
11.
12.     //-- This step assumes a function `get_all_stocks_from_source` exists.
13.     //-- This could be a database query, a call to a cache, or reading a file.
14.     //-- The source contains a list of all available stocks, e.g., [{"symbol": "AAPL", "name": "Apple Inc."}, ...].
15.     **TRY**
16.         **INITIALIZE** `all_stocks` = `get_all_stocks_from_source()`.
17.     **CATCH** Exception `e`:
18.         //-- Log the error that occurred while fetching stock data.
19.         LOG_ERROR("Failed to retrieve stock list from source", `e`).
20.         **RETURN** `matching_stocks`. //-- Return empty list on data source failure.
21.     **END TRY**
22.
23.     //-- TDD Anchor: search_by_symbol_partial_match & search_by_name_partial_match
24.     //-- Iterate through all stocks to find matches.
25.     **FOR EACH** `stock` **IN** `all_stocks`:
26.         **INITIALIZE** `normalized_symbol` = `stock.symbol` converted to lowercase.
27.         **INITIALIZE** `normalized_name` = `stock.name` converted to lowercase.
28.
29.         **IF** `normalized_symbol` contains `normalized_query` **OR** `normalized_name` contains `normalized_query`:
30.             //-- TDD Anchor: result_format_is_correct
31.             //-- Create a dictionary with the specified format.
32.             **CREATE** `result_stock` as a Dictionary.
33.             **SET** `result_stock["symbol"]` = `stock.symbol`.
34.             **SET** `result_stock["name"]` = `stock.name`.
35.
36.             **APPEND** `result_stock` to `matching_stocks`.
37.         **END IF**
38.     **END FOR**
39.
40.     //-- TDD Anchor: search_with_no_matches
41.     **RETURN** `matching_stocks`.
42.
43. **END FUNCTION**