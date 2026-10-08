-- Rename Kyuubi → LakeInsight on existing catalog JSON.
-- The connector was rebranded; Jackson rejects connection.config.type = 'Kyuubi'
-- because LakeInsightConnection.lakeinsightType only allows 'LakeInsight'.
-- serviceType is a generated column derived from json.

UPDATE dbservice_entity
SET json = jsonb_set(
      jsonb_set(json::jsonb, '{serviceType}', '"LakeInsight"'),
      '{connection,config,type}', '"LakeInsight"')
WHERE serviceType = 'Kyuubi'
   OR json #>> '{connection,config,type}' = 'Kyuubi';

UPDATE database_entity
SET json = jsonb_set(json::jsonb, '{serviceType}', '"LakeInsight"')
WHERE json ->> 'serviceType' = 'Kyuubi';

UPDATE database_schema_entity
SET json = jsonb_set(json::jsonb, '{serviceType}', '"LakeInsight"')
WHERE json ->> 'serviceType' = 'Kyuubi';

UPDATE table_entity
SET json = jsonb_set(json::jsonb, '{serviceType}', '"LakeInsight"')
WHERE json ->> 'serviceType' = 'Kyuubi';

UPDATE stored_procedure_entity
SET json = jsonb_set(json::jsonb, '{serviceType}', '"LakeInsight"')
WHERE json ->> 'serviceType' = 'Kyuubi';

UPDATE ingestion_pipeline_entity
SET json = jsonb_set(json::jsonb, '{sourceConfig,serviceConnection,config,type}', '"LakeInsight"')
WHERE json #>> '{sourceConfig,serviceConnection,config,type}' = 'Kyuubi';
