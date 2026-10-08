-- Rename Kyuubi → LakeInsight on existing catalog JSON.
-- The connector was rebranded; Jackson rejects connection.config.type = 'Kyuubi'
-- because LakeInsightConnection.lakeinsightType only allows 'LakeInsight'.
-- serviceType is a generated column derived from json.

UPDATE dbservice_entity
SET json = JSON_SET(
      JSON_SET(json, '$.serviceType', 'LakeInsight'),
      '$.connection.config.type', 'LakeInsight')
WHERE serviceType = 'Kyuubi'
   OR JSON_UNQUOTE(JSON_EXTRACT(json, '$.connection.config.type')) = 'Kyuubi';

UPDATE database_entity
SET json = JSON_SET(json, '$.serviceType', 'LakeInsight')
WHERE JSON_UNQUOTE(JSON_EXTRACT(json, '$.serviceType')) = 'Kyuubi';

UPDATE database_schema_entity
SET json = JSON_SET(json, '$.serviceType', 'LakeInsight')
WHERE JSON_UNQUOTE(JSON_EXTRACT(json, '$.serviceType')) = 'Kyuubi';

UPDATE table_entity
SET json = JSON_SET(json, '$.serviceType', 'LakeInsight')
WHERE JSON_UNQUOTE(JSON_EXTRACT(json, '$.serviceType')) = 'Kyuubi';

UPDATE stored_procedure_entity
SET json = JSON_SET(json, '$.serviceType', 'LakeInsight')
WHERE JSON_UNQUOTE(JSON_EXTRACT(json, '$.serviceType')) = 'Kyuubi';

UPDATE ingestion_pipeline_entity
SET json = JSON_SET(json, '$.sourceConfig.serviceConnection.config.type', 'LakeInsight')
WHERE JSON_UNQUOTE(JSON_EXTRACT(json, '$.sourceConfig.serviceConnection.config.type')) = 'Kyuubi';
