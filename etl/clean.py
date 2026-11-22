"""Clean all raw CSV data and write the cleaned datasets."""

from pathlib import Path
import pandas as pd  # type: ignore[import-untyped]

def clean_restaurants(restaurants: pd.DataFrame) -> pd.DataFrame:
    """Clean restaurant data."""

    restaurants = restaurants.copy()

    # Remove unnecessary columns
    columns_to_remove = [
        'OBJECTID', 'X', 'Y', 'GEOCODESTATUS', 'PERMITID', 'SHAPE'
    ]
    restaurants.drop(
        columns=columns_to_remove,
        errors='ignore',
        inplace=True
    )

    # Standardize text columns
    text_columns = [
        'NAME', 'ADDRESS1', 'ADDRESS2', 'CITY',
        'POSTALCODE', 'PHONENUMBER', 'FACILITYTYPE'
    ]

    for column in text_columns:
        if column in restaurants.columns:
            restaurants[column] = (
                restaurants[column]
                .astype('string')
                .str.strip()
                .str.title()
            )

    # Standardize state abbreviations
    if 'STATE' in restaurants.columns:
        restaurants['STATE'] = (
            restaurants['STATE']
            .astype('string')
            .str.strip()
            .str.upper()
        )

    # Remove rows with missing required values
    required_columns = [
        'HSISID', 'NAME', 'ADDRESS1', 'CITY', 'STATE', 'POSTALCODE'
    ]

    for column in required_columns:
        if column in restaurants.columns:
            restaurants = restaurants[
                restaurants[column].notna()
                & restaurants[column].str.strip().ne('')
            ]

    # Remove duplicate restaurant IDs
    if 'HSISID' in restaurants.columns:
        restaurants = restaurants.drop_duplicates(
            subset='HSISID',
            keep='first'
        )

    # Standardize postal codes
    if 'POSTALCODE' in restaurants.columns:
        restaurants['POSTALCODE'] = (
            restaurants['POSTALCODE']
            .astype('string')
            .str.extract(r'^(\d{5})', expand=False)
            .fillna('00000')
        )

    # Remove numbers from facility type
    if 'FACILITYTYPE' in restaurants.columns:
        restaurants['FACILITYTYPE'] = (
            restaurants['FACILITYTYPE']
            .str.replace(r'^[^A-Za-z]*', '', regex=True)
            .str.strip()
        )

    # Standardize restaurant opening dates
    if 'RESTAURANTOPENDATE' in restaurants.columns:
        restaurants['RESTAURANTOPENDATE'] = pd.to_datetime(
            restaurants['RESTAURANTOPENDATE'],
            errors='coerce'
        ).dt.strftime('%Y-%m-%d')

    return restaurants

def clean_inspections(inspections: pd.DataFrame) -> pd.DataFrame:
    """Clean inspection data."""

    inspections = inspections.copy()

    # Remove unnecessary columns
    columns_to_remove = [
        'OBJECTID', 'PERMITID'
    ]
    inspections.drop(
        columns=columns_to_remove,
        errors='ignore',
        inplace=True
    )

    # Standardize text columns
    text_columns = [
        'DESCRIPTION', 'INSPECTOR'
    ]

    for column in text_columns:
        if column in inspections.columns:
            inspections[column] = (
                inspections[column]
                .astype('string')
                .str.strip()
                .str.title()
            )

    # Remove rows with missing required values
    for column in ('HSISID', 'SCORE', 'DATE_'):
        if column in inspections.columns:
            inspections = inspections[inspections[column].notna()]

    # Standardize dates and rename the date column
    if 'DATE_' in inspections.columns:
        inspections['DATE_'] = pd.to_datetime(
            inspections['DATE_'],
            errors='coerce'
        ).dt.strftime('%Y-%m-%d')
        inspections = inspections.rename(columns={'DATE_': 'DATE'})

    # Remove the prefix from inspection types
    if 'TYPE' in inspections.columns:
        inspections['TYPE'] = (
            inspections['TYPE']
            .astype('string')
            .str.strip()
            .str.replace(r'^[^A-Za-z]*', '', regex=True)
            .str.title()
        )

    return inspections

def clean_violations(violations: pd.DataFrame) -> pd.DataFrame:
    """Clean violation data."""

    violations = violations.copy()

    # Remove unnecessary columns
    columns_to_remove = [
        'OBJECTID', 'CATEGORY', 'STATECODE', 'CDCRISKFACTOR',
        'CDCDATAITEM', 'PERMITID'
    ]
    violations.drop(
        columns=columns_to_remove,
        errors='ignore',
        inplace=True
    )

    # Standardize text columns
    text_columns = [
        'HSISID', 'VIOLATIONCODE', 'SEVERITY', 'SHORTDESC',
        'INSPECTEDBY', 'COMMENTS', 'OBSERVATIONTYPE', 'VIOLATIONTYPE'
    ]

    for column in text_columns:
        if column in violations.columns:
            violations[column] = (
                violations[column]
                .astype('string')
                .str.strip()
                .str.replace(r'\s+', ' ', regex=True)
            )

    # Standardize case for categorical text fields
    if 'SEVERITY' in violations.columns:
        violations['SEVERITY'] = violations['SEVERITY'].str.title()
    if 'VIOLATIONTYPE' in violations.columns:
        violations['VIOLATIONTYPE'] = violations['VIOLATIONTYPE'].str.upper()

    # Standardize dates and rename the date column
    if 'INSPECTDATE' in violations.columns:
        violations['INSPECTDATE'] = pd.to_datetime(
            violations['INSPECTDATE'],
            errors='coerce'
        ).dt.strftime('%Y-%m-%d')
        violations = violations.rename(columns={'INSPECTDATE': 'DATE'})

    # Convert POINTVALUE to numeric, remove rows with missing or invalid values
    if 'POINTVALUE' in violations.columns:
        violations['POINTVALUE'] = pd.to_numeric(
            violations['POINTVALUE'],
            errors='coerce'
        )
        violations = violations[violations['POINTVALUE'].notna()]

    # Convert QUESTIONNO to numeric
    if 'QUESTIONNO' in violations.columns:
        violations['QUESTIONNO'] = pd.to_numeric(
            violations['QUESTIONNO'],
            errors='coerce'
        )

    # Remove rows with missing required values
    required_columns = [
        'HSISID', 'DATE', 'QUESTIONNO', 'INSPECTEDBY',
        'VIOLATIONCODE', 'SEVERITY'
    ]

    for column in required_columns:
        if column in violations.columns:
            if pd.api.types.is_object_dtype(violations[column].dtype) or (
                pd.api.types.is_string_dtype(violations[column].dtype)
            ):
                violations[column] = (
                    violations[column]
                    .replace(r'(?i)^not provided$', pd.NA, regex=True)
                    .replace(r'^\s*$', pd.NA, regex=True)
                )
            violations = violations[violations[column].notna()]

    return violations

def main() -> None:
    """Clean inspections, restaurants, and violations in one run."""
    project_dir = Path(__file__).resolve().parent.parent
    raw_dir = project_dir / 'data' / 'raw'
    clean_dir = project_dir / 'data' / 'clean'
    clean_dir.mkdir(parents=True, exist_ok=True)

    inspections = pd.read_csv(
        raw_dir / 'Food_Inspections.csv',
        dtype={'HSISID': 'string', 'PERMITID': 'string'},
        encoding='utf-8-sig',
    )
    cleaned_inspections = clean_inspections(inspections)
    cleaned_inspections.to_csv(clean_dir / 'inspections.csv', index=False)

    restaurants = pd.read_csv(
        raw_dir / 'Restaurants_in_Wake_County.csv',
        dtype={
            'HSISID': 'string',
            'POSTALCODE': 'string',
            'PERMITID': 'string',
        },
        encoding='utf-8-sig',
    )
    cleaned_restaurants = clean_restaurants(restaurants)
    cleaned_restaurants.to_csv(clean_dir / 'restaurants.csv', index=False)

    violations = pd.read_csv(
        raw_dir / 'Food_Inspection_Violations.csv',
        dtype={'HSISID': 'string', 'PERMITID': 'string'},
        encoding='utf-8-sig',
    )
    cleaned_violations = clean_violations(violations)
    cleaned_violations.to_csv(clean_dir / 'violations.csv', index=False)

if __name__ == '__main__':
    main()
