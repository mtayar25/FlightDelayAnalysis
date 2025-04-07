-- models/flight_performance.sql


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