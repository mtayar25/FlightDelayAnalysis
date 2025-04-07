
import pandas as pd
import os


if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer


@transformer
def transform_data(data, *args, **kwargs):
    """
    Loads data from a CSV, performs data cleaning, and returns a Pandas DataFrame.
    """
    tmp_dir = '/tmp'
    csv_files = [f for f in os.listdir(tmp_dir) if f.endswith('.csv')]
    if not csv_files:
        raise FileNotFoundError("No CSV files found in /tmp directory.")
    elif len(csv_files) > 1:
        print("Warning: Multiple CSV files found in /tmp. Using the first one.")
    csv_file_name = csv_files[0]
    local_csv_path = os.path.join(tmp_dir, csv_file_name)

    df = pd.read_csv(local_csv_path)

    # 1. Verify FL_DATE as datetime and handle errors
    try:
        df['FL_DATE'] = pd.to_datetime(df['FL_DATE'], errors='raise')
    except ValueError as e:
        print(f"Error converting FL_DATE to datetime: {e}")
        raise e

    # 2. Remove rows with missing values in FL_DATE and AIRLINE
    df = df.dropna(subset=['FL_DATE', 'AIRLINE'])

    return df



@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'