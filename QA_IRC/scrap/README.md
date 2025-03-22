# Bloomberg Tax IRC Scraper

This is a web scraper for [Bloomberg Tax IRC](https://irc.bloombergtax.com), a site that provides free access to the full text of the current Internal Revenue Code.

## How It Works
The scraper recursively traverses hyperlinks in HTML pages, following links until it reaches a final page. Once there, it attempts to extract text and tables from the content.

## Notes
- Not all text is extracted from the final HTML pages:
  1. The **amendments** section on each page is not extracted.
  2. Some sections contain no extractable text, such as [this example](https://irc.bloombergtax.com/public/uscode/doc/irc/section_1013).

- The scraper generates two log files:
  - **`extracts_links_log.txt`** – Lists the final sections where **any** text was successfully extracted.
  - **`unextracts_links_log.txt`** – Lists sections where **no** text was extracted.

## Installation & Usage
python scrapper.py
