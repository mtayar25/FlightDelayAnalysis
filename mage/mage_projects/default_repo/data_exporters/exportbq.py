

from mage_ai.settings.repo import get_repo_path
from mage_ai.io.bigquery import BigQuery
from mage_ai.io.config import ConfigFileLoader
from pandas import DataFrame
from os import path

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data_to_big_query(df: DataFrame, **kwargs) -> None:
    """
    Export data to a BigQuery table with monthly partitioning on FL_DATE.
    Infers column names and types from the DataFrame.
    """
    # Define table ID 
    project_id = 'pelagic-range-454520-i9'
    dataset_id = 'FlightDelayMT2025_dataset'
    table_name = 'FlightDelays'
    table_id = f'{project_id}.{dataset_id}.{table_name}'
    
    # Path to configuration file
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    
    # BigQuery client instance
    bigquery_client = BigQuery.with_config(ConfigFileLoader(config_path, config_profile))
    
    # Infer schema from DataFrame
    schema = ', '.join([f'{col} {dtype}' for col, dtype in zip(df.columns, df.dtypes.map(lambda x: x.name.upper()))])
    
    # SQL to create a partitioned table if it doesn't exist
    create_table_sql = f"""
        CREATE TABLE `{table_id}` (
            {schema}
        )
        PARTITION BY DATE_TRUNC(FL_DATE, MONTH)
        OPTIONS (
            require_partition_filter = TRUE
        )
    """
    
    # Execute the SQL to create the table
    bigquery_client.execute(create_table_sql)
    
    # Export data to the newly created table
    bigquery_client.export(
        df,
        table_id,
        if_exists='append',  # Append data if the table already exists
        overwrite_types=None  # Adjust column types if necessary
    )
