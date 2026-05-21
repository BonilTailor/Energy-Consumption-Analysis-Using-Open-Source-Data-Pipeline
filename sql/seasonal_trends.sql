-- ============================================================
-- Seasonal Energy Consumption Trends
-- ============================================================

CREATE OR REPLACE TABLE
  `energy_analytics.seasonal_trends`
AS

SELECT

    season,

    COUNT(*) AS total_records,

    ROUND(
        SUM(energy_consumption),
        2
    ) AS total_consumption,

    ROUND(
        AVG(energy_consumption),
        2
    ) AS avg_consumption,

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
    ) AS consumption_variability,

    COUNT(DISTINCT household_id)
        AS unique_households,

    COUNTIF(anomaly_label = 'anomaly')
        AS anomaly_events,

    COUNTIF(is_peak_hour = 1)
        AS peak_hour_events

FROM
  `energy_analytics.feature_engineered_data`

GROUP BY
    season

ORDER BY
    avg_consumption DESC;