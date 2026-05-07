from metadata.ingestion.source.database.kyuubi.lineage import KyuubiLineageSource
from metadata.ingestion.source.database.kyuubi.metadata import KyuubiSource
from metadata.utils.service_spec.default import DefaultDatabaseSpec

ServiceSpec = DefaultDatabaseSpec(
    metadata_source_class=KyuubiSource,
    lineage_source_class=KyuubiLineageSource,
)
