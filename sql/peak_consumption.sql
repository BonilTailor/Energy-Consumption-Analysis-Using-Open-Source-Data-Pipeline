-- ============================================================
-- Peak Consumption Analytics
-- ============================================================

CREATE OR REPLACE TABLE
  `energy_analytics.peak_consumption_analysis`
AS

SELECT

    hour,

    COUNT(*) AS total_readings,

    ROUND(
        AVG(energy_consumption),
        2
    ) AS avg_consumption,

    ROUND(
        SUM(energy_consumption),
        2
    ) AS total_consumption,

    ROUND(
        MAX(energy_consumption),
        2
    ) AS peak_consumption,

    ROUND(
        MIN(energy_consumption),
        2
    ) AS minimum_consumption,

    ROUND(
        STDDEV(energy_consumption),
        2
    ) AS hourly_variability,

    COUNTIF(is_peak_hour = 1)
        AS peak_hour_records,

    COUNTIF(anomaly_label = 'anomaly')
        AS anomaly_count

FROM
  `energy_analytics.feature_engineered_data`

GROUP BY
    hour

ORDER BY
    avg_consumption DESC;