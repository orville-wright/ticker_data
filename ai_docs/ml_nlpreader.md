# ml_nlpreader Mermaid Diagram

This diagram visualizes the classes and their relationships in the `ml_nlpreader.py` file.

```mermaid
classDiagram
    class ml_nlpreader {
        +args: list
        +ml_yfn_dataset: yfnews_reader
        +yfn_uh: url_hinter
        +yti: int
        +cycle: int
        +__init__(yti, global_args)
        +nlp_read_all(global_args)
        +nlp_read_one(news_symbol, global_args)
        +nlp_summary(yti, ml_idx)
    }

    class yfnews_reader {
        +share_hinter(url_hinter)
        +update_headers(target)
        +form_endpoint(target)
        +do_simple_get()
        +scan_news_feed(target, depth, render, index)
        +eval_article_tags(target)
        +interpret_page(ml_idx, sn_row)
        +eval_news_feed_stories(symbol)
    }

    class url_hinter {
        +uhinter(level, url)
        +confidence_lvl(hint)
    }

    class y_topgainers {
        +get_topg_data()
        +build_tg_df0()
        +build_top10()
    }

    class y_cookiemonster {
        +get_js_data(hpath)
    }

    ml_nlpreader --|> yfnews_reader : instantiates
    ml_nlpreader --|> url_hinter : instantiates
    ml_nlpreader --|> y_topgainers : instantiates
    ml_nlpreader --|> y_cookiemonster : instantiates

    ml_nlpreader ..> yfnews_reader : calls methods
    ml_nlpreader ..> url_hinter : calls methods
    ml_nlpreader ..> y_topgainers : calls methods
    ml_nlpreader ..> y_cookiemonster : calls methods
    yfnews_reader ..> url_hinter : uses
```

### Class Descriptions:

*   **ml_nlpreader**: The main class that orchestrates the process of reading and analyzing news articles. It uses instances of other classes to fetch data, get URL hints, and handle cookies.
*   **yfnews_reader**: Responsible for reading news from Yahoo Finance. It interacts with `url_hinter` to analyze URLs.
*   **url_hinter**: Provides hints and confidence levels for URLs to help classify them.
*   **y_topgainers**: Fetches data about top-gaining stocks.
*   **y_cookiemonster**: Manages cookies for web scraping sessions.