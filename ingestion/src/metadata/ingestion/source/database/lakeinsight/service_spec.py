from metadata.ingestion.source.database.lakeinsight.lineage import LakeInsightLineageSource
from metadata.ingestion.source.database.lakeinsight.metadata import LakeInsightSource
from metadata.utils.service_spec.default import DefaultDatabaseSpec

ServiceSpec = DefaultDatabaseSpec(
    metadata_source_class=LakeInsightSource,
    lineage_source_class=LakeInsightLineageSource,
)
