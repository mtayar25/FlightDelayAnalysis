if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter




from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.google_cloud_storage import GoogleCloudStorage

@data_exporter
def export_data(data, *args, **kwargs):
    config_path = '/home/src/default_repo/io_config.yaml'
    config_profile = 'default'

    # Load GCS configuration from io_config.yaml
    gcs_client = GoogleCloudStorage.with_config(ConfigFileLoader(config_path, config_profile))
    gcs_client.export(
        data,
        bucket_name='flightdelaymt2025-bucket',
        object_key='flighdelaydata.parquet',
        format='parquet'
    )
