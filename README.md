# Car Finder

A Python script that scrapes used car listings from AutoTrader.ca and Kijiji, merges them into one table and writes a CSV with Excel formulas that score each car on year, mileage and price.

> Archived: no longer maintained. Kept for reference.

## What it does

1. Fetches search result pages from Kijiji (a configurable page range) and one AutoTrader results page, using hard-coded search URLs filtered by location, price, year, mileage and transmission.
2. Parses each listing with BeautifulSoup into a common set of columns: source, date posted, title, description, URL, transmission, location, price, year and mileage. Kijiji's relative dates ("< x hours ago", "Yesterday") are converted to real dates.
3. Collects the rows in a pandas DataFrame and drops duplicates on title, year, mileage and price.
4. Adds score columns written as Excel structured-table formulas, so they calculate once the CSV is opened in Excel and formatted as a table:
   - `YearScore`, `MileageScore`, `PriceScore`: each normalized to 0–1 against the min and max of the result set (newer, lower mileage and cheaper score higher)
   - `TotalScore`: sum of all three
   - `PMScore`: price plus mileage only
5. Saves the result as `YYYY-MM-DD-CarSearchOutput.csv`.

`Request for Offer.docx` is the buyer brief the search was built around: up to 80,000 km, 2010 or newer, up to $8,000, automatic, no accidents, plus a shortlist of models. The two sample CSVs in the repo contain only the header row.

## Tech stack

Python 3, requests, BeautifulSoup 4, pandas.

## Running it

This will almost certainly not work today. Both sites have changed their markup and URLs since 2016, and the script relies on specific CSS class names. `DataFrame.append` has also since been removed from pandas, and `requirements.txt` pins `BeautifulSoup==3.2.1` while the code imports `bs4`.

For reference, the original usage was:

```
pip install requests beautifulsoup4 pandas
# edit AUTOTRADER_URL, KIJIJI_URL, firstPage and lastPage in CarSearch.py
python CarSearch.py
```

## Context

Written in September 2016 to help with a real used car purchase: instead of browsing two sites by hand, pull every matching listing into one spreadsheet and rank them.
