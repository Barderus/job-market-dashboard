import pandas as pd
import re

def load_and_prepare_data(job_path):
    """
    Load and clean job data from the given CSV path.

    Parameters:
        job_path (str): Path to the main job market CSV file.

    Returns:
        df (DataFrame): Cleaned main job market dataset.
    """
    df = pd.read_csv(job_path)

    # Clean and normalize description
    df['Description_clean'] = df['Description'].str.lower().fillna("")

    return df

def extract_salary_range(s):
    # If the salary is missing (NaN), return two None values
    if pd.isna(s):
        return pd.Series([None, None])

    # Remove currency symbols and commas, convert to lowercase for uniformity
    s_clean = s.replace('$', '').replace(',', '').lower()

    # Find all numeric values and their suffixes (k, m)
    match = re.findall(r'(\d+(?:\.\d+)?)([kKmM]?)', s_clean)

    # If no matches are found, return None values
    if not match:
        return pd.Series([None, None])

    values = []
    for val, suffix in match:
        num = float(val)
        # Convert values based on suffix
        if suffix == 'k':
            num *= 1_000
        elif suffix == 'm':
            num *= 1_000_000
        values.append(num)

    # If only one value was found, assume min and max are the same
    if len(values) == 1:
        return pd.Series([values[0], values[0]])
    # If at least two values were found, return the min and max of the first two
    elif len(values) >= 2:
        return pd.Series([min(values[:2]), max(values[:2])])
    else:
        return pd.Series([None, None])


def normalize_salary(value):
    """
    Normalize salary by converting hourly (<= 3 digit) values to annual.
    """
    if pd.isna(value):
        return None
    try:
        digits = len(str(int(value)))
        if digits <= 3:
            return value * 2080  # Hourly → Annual
        return value  # Already Annual
    except:
        return None
