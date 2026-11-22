# SafePlate

SafePlate cleans and prepares Wake County restaurant inspection data for
analysis. The project processes three public CSV datasets: restaurants,
inspections, and inspection violations.

## Project structure

```text
safeplate/
├── data/
│   ├── raw/
│   │   ├── Restaurants_in_Wake_County.csv
│   │   ├── Food_Inspections.csv
│   │   └── Food_Inspection_Violations.csv
│   └── clean/
│       ├── restaurants.csv
│       ├── inspections.csv
│       └── violations.csv
├── etl/
│   └── clean.py
└── README.md
```

- `data/raw/` contains the source CSV downloads.
- `data/clean/` contains the cleaned CSV files produced by the ETL script.
- `etl/clean.py` contains all cleaning functions and the project entry point.

## Source datasets

- [Restaurants in Wake County](https://data-wake.opendata.arcgis.com/datasets/Wake::restaurants-in-wake-county)
- [Food Inspections](https://data-wake.opendata.arcgis.com/datasets/Wake::food-inspections)
- [Food Inspection Violations](https://data-wake.opendata.arcgis.com/datasets/Wake::food-inspection-violations)

The raw dataset names and original columns are:

```text
Restaurants:
OBJECTID, HSISID, NAME, ADDRESS1, ADDRESS2, CITY, STATE, POSTALCODE,
PHONENUMBER, RESTAURANTOPENDATE, FACILITYTYPE, X, Y, GEOCODESTATUS,
PERMITID, SHAPE

Inspections:
OBJECTID, HSISID, SCORE, DATE_, DESCRIPTION, TYPE, INSPECTOR, PERMITID

Violations:
OBJECTID, HSISID, INSPECTDATE, CATEGORY, STATECODE, QUESTIONNO,
VIOLATIONCODE, SEVERITY, SHORTDESC, INSPECTEDBY, COMMENTS, POINTVALUE,
OBSERVATIONTYPE, VIOLATIONTYPE, CDCRISKFACTOR, CDCDATAITEM, PERMITID
```

## Installation

Python 3 and `pip` are required. From the project root, create and activate
a virtual environment:

## Running the cleaner

Place the three source CSV files in `data/raw/`, then run:

```bash
python3 etl/clean.py
```

The script creates `data/clean/` if needed and writes:

- `data/clean/restaurants.csv`
- `data/clean/inspections.csv`
- `data/clean/violations.csv`

## Data cleaning steps

### Restaurants

1. Remove unnecessary columns: `OBJECTID`, `X`, `Y`, `GEOCODESTATUS`,
   `PERMITID`, and `SHAPE`.
2. Trim text and standardize capitalization in names, addresses, city,
   postal codes, phone numbers, and facility types.
3. Convert state abbreviations to uppercase.
4. Remove restaurants with missing or empty required values:
   `HSISID`, `NAME`, `ADDRESS1`, `CITY`, `STATE`, and `POSTALCODE`.
5. Remove duplicate restaurant records by keeping the first row for each
   `HSISID`.
6. Reduce postal codes to the first five digits, so ZIP+4 values such as
   `27608-1710` become `27608`. Fill missing or invalid postal codes with
   `00000`.
7. Remove numeric prefixes from facility types, leaving text beginning with
   the first letter.
8. Convert restaurant opening dates to `YYYY-MM-DD`.

### Inspections

1. Remove unnecessary columns: `OBJECTID` and `PERMITID`.
2. Trim and title-case inspection descriptions and inspector names.
3. Remove rows with missing `HSISID`, `SCORE`, or `DATE_` values.
4. Convert `DATE_` to `YYYY-MM-DD` and rename it to `DATE`.
5. Remove numeric and punctuation prefixes from inspection types and
   title-case the remaining text.

### Violations

1. Remove unnecessary columns: `OBJECTID`, `CATEGORY`, `STATECODE`,
   `CDCRISKFACTOR`, `CDCDATAITEM`, and `PERMITID`.
2. Trim text and collapse repeated whitespace in violation codes, severity,
   descriptions, inspectors, comments, and violation types.
   Treat `Not Provided` as missing text.
3. Convert `INSPECTDATE` to `YYYY-MM-DD` and rename it to `DATE`.
4. Convert `POINTVALUE` to numeric values and remove missing or invalid
   values.
5. Convert `QUESTIONNO` to numeric and remove missing or invalid values.
6. Title-case `SEVERITY` and upper-case `VIOLATIONTYPE`.
7. Remove rows with missing required values: `HSISID`, `DATE`, `QUESTIONNO`,
   `INSPECTEDBY`, `VIOLATIONCODE`, and `SEVERITY`. Rows using `Not Provided`
   in any required field are removed.
