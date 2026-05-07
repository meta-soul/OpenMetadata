#  Copyright 2025 Collate
#  Licensed under the Collate Community License, Version 1.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  https://github.com/open-metadata/OpenMetadata/blob/main/ingestion/LICENSE
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""
Kyuubi source methods.

Kyuubi uses Spark as the underlying execution engine and communicates
via the HiveServer2 Thrift protocol. The metadata extraction customizes
the Hive SQLAlchemy dialect methods to handle Spark's DESCRIBE TABLE
output format, which differs from Hive's DESCRIBE FORMATTED format.
"""

import traceback

from pyhive.sqlalchemy_hive import HiveDialect
from sqlalchemy.engine.reflection import Inspector

from metadata.generated.schema.entity.data.table import TableType
from metadata.generated.schema.entity.services.connections.database.kyuubiConnection import (
    KyuubiConnection,
)
from metadata.generated.schema.metadataIngestion.workflow import (
    Source as WorkflowSource,
)
from metadata.ingestion.api.steps import InvalidSourceException
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.ingestion.source.database.common_db_source import CommonDbSourceService
from metadata.ingestion.source.database.kyuubi.utils import (
    get_columns,
    get_table_comment,
    get_table_names,
    get_view_definition,
    get_view_names,
)
from metadata.utils.logger import ingestion_logger

logger = ingestion_logger()

HiveDialect.get_columns = get_columns
HiveDialect.get_table_comment = get_table_comment


class KyuubiSource(CommonDbSourceService):
    """
    Implements the necessary methods to extract
    Database metadata from Kyuubi Source (Spark-based execution).
    """

    service_connection: KyuubiConnection

    @classmethod
    def create(cls, config_dict, metadata: OpenMetadata, pipeline_name: str | None = None):
        config = WorkflowSource.model_validate(config_dict)
        connection: KyuubiConnection = config.serviceConnection.root.config
        if not isinstance(connection, KyuubiConnection):
            raise InvalidSourceException(f"Expected KyuubiConnection, but got {connection}")
        return cls(config, metadata)

    def prepare(self):
        """
        Monkey-patch the HiveDialect methods to handle Spark's DESCRIBE TABLE
        output format which differs from Hive's format.

        Kyuubi uses Spark as its execution engine, so DESCRIBE TABLE and
        SHOW TABLES output follow Spark conventions:
        - SHOW TABLES returns 3 columns (namespace, tableName, isTemporary)
        - DESCRIBE TABLE EXTENDED has Comment in col_name column
        """
        HiveDialect.get_table_names = get_table_names
        HiveDialect.get_view_names = get_view_names
        HiveDialect.get_view_definition = get_view_definition

    def get_schema_definition(
        self, table_type: str, table_name: str, schema_name: str, inspector: Inspector
    ) -> str | None:
        """
        Get the DDL statement or View Definition for a table
        """
        try:
            if self.source_config.includeDDL or table_type in (
                TableType.View,
                TableType.MaterializedView,
            ):
                schema_definition = inspector.get_view_definition(table_name, schema_name)
                if schema_definition is not None:
                    return str(schema_definition).strip()
        except NotImplementedError:
            logger.warning("Schema definition not implemented")

        except Exception as exc:
            logger.debug(traceback.format_exc())
            logger.warning(f"Failed to fetch schema definition for {table_name}: {exc}")
        return None
