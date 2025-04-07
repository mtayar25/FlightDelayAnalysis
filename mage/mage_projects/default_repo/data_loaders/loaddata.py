
from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd
import os

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader

@data_loader
def load_and_upload_kaggle_data(**kwargs):
    """
    Custom Mage block to load Kaggle CSV data and upload it to GCS in Parquet format.
    """
    # Step 1: Authenticate Kaggle API

    api = KaggleApi()
    api.authenticate()
    
    # Step 2: Download Kaggle dataset (replace with your dataset name)
    dataset = "patrickzel/flight-delay-and-cancellation-dataset-2019-2023"  # Replace with your Kaggle dataset name
    api.dataset_download_files(dataset, path="/tmp", unzip=True)


    #( return an empty data frame")
    data = pd.DataFrame({'A' : []})
    print ("done")
    return data

