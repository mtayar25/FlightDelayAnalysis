# Flight Delay Analysis Project (2020-2023)

## 🚀 Project Overview
This project analyzes flight delay data from 2020 to 2023 using the **Flight Delay and Cancellation Dataset (2019-2023)** from Kaggle. The goal is to uncover trends and insights into flight delays and cancellations during this period. The pipeline leverages modern data tools for ingestion, transformation, and visualization.

### Key Features:
- **Data Source**: Kaggle Flight Delay and Cancellation Dataset (2019-2023)
- **Tools Used**:
  - **Terraform**: Infrastructure-as-code for BigQuery setup
  - **Mage**: Data pipeline orchestration
  - **dbt**: Transformations and analytics
  - **Looker Studio**: Dashboard creation for insights visualization
- **Core Metrics**:
  - Flight delay classification (`isdelayed` flag)
  - Temporal analysis using `FL_DATE` components

---

## 📂 Repository Structure
3 folders were create to include the configuration of tools used : terraform, mage and dbt. Google cloud service account was added in secrets folder and used by the tools.

---

## 🛠️ Tools & Workflow

### **Terraform**
- Provisioned Google Cloud Platform resources using variables for configuration
- Defined all resource names in `variables.tf` for consistency and reusability


### **Mage**
- Built a pipeline (loadkaggleexportbq) with 3 blocks:

   1. **LoadData **: Loader block that downloads the kaggle dataset to `/tmp`.
     
  ``` py
    
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


  ```
 2. **CleanData **: Transformer block that process and clean the dataset (enforces data types and remove null rows).
  
  ``` py

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
 ``` 
 3. **ExportBQ**: Uploads the data into BigQuery table and activate partioning by month.
  
 ``` py

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
 ``` 


### **dbt Transformations**
1. Added `isdelayed` column to classify delayed flights.

2. Extracted year, month, and day of week from `FL_DATE` column
3. The results are materialized as a view in BQ : flightperformance
 ``` sql
-- models/flight_performance.sql

{{ config(materialized='table') }}
--WITH base AS (
    SELECT
        FL_DATE,
        AIRLINE,
        ARR_DELAY,
        DEP_DELAY,
        (DEP_DELAY+ARR_DELAY) as Total_Delay,
        CASE When (ARR_DELAY >0 OR DEP_DELAY >0) THEN 1 else 0 END as IsDelayed,

 

    FORMAT_TIMESTAMP('%A', TIMESTAMP(FL_DATE)) as 
   day_of_week,  -- Extract day name
        EXTRACT(MONTH FROM FL_DATE) AS month,                       -- Extract month number
        EXTRACT(YEAR FROM FL_DATE) AS year                         -- Extract year
    FROM 
        `pelagic-range-454520-i9.FlightDelayMT2025_dataset.FlightDelays`
```
---

### **Looker Studio**
Created a dashboard for visualizing insights:
1. Connected Looker Studio directly to BigQuery.
2. Visualized metrics such as delay frequency, temporal trends, and carrier performance.

#### Dashboard Components:
- **Delay Classification**:
    - Used a Pie chart to reprensent the % of delayed flights.


- **Temporal Analysis**:
    - Used  two bar charts to represent the average delay per year and day of the week

- **Carrier Performance**:
    - Used a bar chart to represent the average delay per airline.

![image](https://github.com/user-attachments/assets/8aa0988f-4251-48f7-ad63-717bb0bf3461)



## 🔗 Setup Guide
### in the root directory of the project add a directory called secrets and put inside the credentional for kaggle (kaggle.json) and Google CLoud
platform (gcp.json)

### Step 1: Terraform Setup
1. Initialize Terraform:
terraform init
terraform apply -auto-approve

text
*Value to change*: Update `variables.tf` with your GCP project ID.

---

### Step 2: Mage Pipeline Execution
1. start Mage with the command `docker-compose up -d` (make sure to put the gcp service accoount credential  file in secrets or modify the docker compose for volume mapping:

2. run the pipeline  `load_kaggle_export_bq` with the following link on your browser:
 `http://localhost:6789/pipelines/loadkaggleexportbq`


---

### Step 3: dbt Configuration & Run
1. Configure dbt profile to modify the location of the gcp crendential file:
2. Run the dbt service with with the command `docker-compose up -d`  , the model will atutomaically execute

---

### Step 4: Looker Studio Dashboard Creation
1. Connect Looker Studio to BigQuery.
2. here is a link to the dashboard created.
`https://lookerstudio.google.com/reporting/cfedf29c-202f-439a-a388-0bfd849b5a8d`

---

## 💡 Insights & Findings

1. **Delayed flights ratio**:
   - Over 40% of flights are delayed.
   
2. **Carrier Variance**:
   - There is 30 mins delay variance between the top and bottom airline with the top having around 90 mins average delay.

3. **Temporal**:
   - The average delay seems to be uniform across the days of the week with 2023 presenting the highest average dealy.

---


