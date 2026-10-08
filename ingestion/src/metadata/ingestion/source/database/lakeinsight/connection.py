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
Source connection handler for LakeInsight.

LakeInsight uses the Hive Thrift protocol (HS2), so it connects via pyhive
with the Hive SQLAlchemy dialect. Authentication methods (LDAP, KERBEROS,
NOSASL, NONE, CUSTOM) and SSL configuration follow the same pattern as
the Hive connector.
"""

from urllib.parse import quote_plus

# Monkey-patch pyhive to use our custom LakeInsight connection class
import pyhive.hive
from pydantic import SecretStr
from sqlalchemy.engine import Engine

from metadata.generated.schema.entity.automations.workflow import (
    Workflow as AutomationWorkflow,
)
from metadata.generated.schema.entity.services.connections.database.lakeinsightConnection import (
    LakeInsightConnection,
    LakeinsightScheme,
)
from metadata.generated.schema.entity.services.connections.testConnectionResult import (
    TestConnectionResult,
)
from metadata.ingestion.connections.builders import (
    create_generic_db_connection,
    get_connection_args_common,
    get_connection_options_dict,
    init_empty_connection_arguments,
)
from metadata.ingestion.connections.test_connections import (
    test_connection_db_schema_sources,
)
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.ingestion.source.database.lakeinsight.custom_lakeinsight_connection import (
    CustomLakeInsightConnection,
)
from metadata.utils.constants import THREE_MIN
from metadata.utils.ssl_manager import check_ssl_and_init

pyhive.hive.Connection = CustomLakeInsightConnection


def get_connection_url(connection: LakeInsightConnection) -> str:
    """
    Build the URL handling auth requirements.

    LakeInsight uses the Hive Thrift protocol, so the connection URL
    follows the same pattern as Hive (pyhive dialect).
    """
    url = f"{connection.scheme.value}://"
    if connection.username and connection.auth and connection.auth.value in ("LDAP", "CUSTOM"):
        url += quote_plus(connection.username)
        if not connection.password:
            connection.password = SecretStr("")
        url += f":{quote_plus(connection.password.get_secret_value())}"
        url += "@"

    elif connection.username:
        url += quote_plus(connection.username)
        if connection.password:
            url += f":{quote_plus(connection.password.get_secret_value())}"
        url += "@"

    url += connection.hostPort
    url += f"/{connection.databaseSchema}" if connection.databaseSchema else ""

    options = get_connection_options_dict(connection)
    if options:
        params = "&".join(f"{key}={quote_plus(value)}" for (key, value) in options.items() if value)
        url = f"{url}?{params}"
    if connection.authOptions:
        return f"{url};{connection.authOptions}"
    return url


def get_connection(connection: LakeInsightConnection) -> Engine:
    """
    Create connection to LakeInsight via Hive Thrift protocol.
    """

    if connection.auth:
        if not connection.connectionArguments:
            connection.connectionArguments = init_empty_connection_arguments()
        auth_key = (
            "auth"
            if connection.scheme in {LakeinsightScheme.hive, LakeinsightScheme.hive_http, LakeinsightScheme.hive_https}
            else "auth_mechanism"
        )
        connection.connectionArguments.root[auth_key] = connection.auth.value

    if connection.kerberosServiceName:
        if not connection.connectionArguments:
            connection.connectionArguments = init_empty_connection_arguments()
        connection.connectionArguments.root["kerberos_service_name"] = connection.kerberosServiceName

    ssl_manager = check_ssl_and_init(connection)
    if ssl_manager:
        connection = ssl_manager.setup_ssl(connection)
        connection._ssl_manager = ssl_manager

    if hasattr(connection, "useSSL") and connection.useSSL:
        if not connection.connectionArguments:
            connection.connectionArguments = init_empty_connection_arguments()
        connection.connectionArguments.root["use_ssl"] = True

    return create_generic_db_connection(
        connection=connection,
        get_connection_url_fn=get_connection_url,
        get_connection_args_fn=get_connection_args_common,
    )


def test_connection(
    metadata: OpenMetadata,
    engine: Engine,
    service_connection: LakeInsightConnection,
    automation_workflow: AutomationWorkflow | None = None,
    timeout_seconds: int | None = THREE_MIN,
) -> TestConnectionResult:
    """
    Test connection. This can be executed either as part
    of a metadata workflow or during an Automation Workflow
    """
    return test_connection_db_schema_sources(
        metadata=metadata,
        engine=engine,
        service_connection=service_connection,
        automation_workflow=automation_workflow,
        timeout_seconds=timeout_seconds,
    )
