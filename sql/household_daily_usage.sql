-- Household Daily Energy Usage Aggregation

CREATE OR REPLACE TABLE
  `energy_analytics.household_daily_usage`
AS

SELECT
    household_id,

    DATE(timestamp) AS usage_date,

    COUNT(*) AS total_readings,

    ROUND(
        SUM(energy_consumption),
        2
    ) AS total_daily_consumption,

    ROUND(
        AVG(energy_consumption),
        2
    ) AS avg_daily_consumption,

    ROUND(
        MAX(energy_consumption),
        2
    ) AS max_daily_consumption,

    ROUND(
        MIN(energy_consumption),
        2
    ) AS min_daily_consumption,

    ROUND(
        STDDEV(energy_consumption),
        2
    ) AS consumption_stddev,

    MAX(is_peak_hour) AS peak_hour_detected,

    MAX(is_weekend) AS weekend_usage

FROM
  `energy_analytics.feature_engineered_data`

GROUP BY
    household_id,
    usage_date

ORDER BY
    usage_date,
    household_id;
