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
Custom LakeInsight Thrift connection that handles Spark-specific behavior.
LakeInsight uses Spark as the underlying execution engine and communicates
via the HiveServer2 Thrift protocol. This connection is adapted from
the Hive custom connection and works with pyhive over Thrift.
"""

import contextlib
import getpass
import ssl

import thrift.protocol.TBinaryProtocol
import thrift.transport.TSocket
import thrift.transport.TTransport
from pyhive.hive import Connection as BaseConnection
from pyhive.hive import _check_status, get_installed_sasl
from TCLIService import TCLIService, ttypes


class CustomLakeInsightConnection(BaseConnection):
    """Custom LakeInsight connection that integrates puretransport and SSL certificate support"""

    def __init__(  # noqa: C901
        self,
        host=None,
        port=None,
        scheme=None,
        username=None,
        database="default",
        auth=None,
        configuration=None,
        kerberos_service_name=None,
        password=None,
        check_hostname=None,
        ssl_cert=None,
        thrift_transport=None,
        use_ssl=False,
        ssl_certfile=None,
        ssl_keyfile=None,
        ssl_ca_certs=None,
        ssl_cert_reqs=None,
        ssl_check_hostname=None,
    ):
        """Connect to LakeInsight via HiveServer2 Thrift protocol"""

        # Handle HTTPS scheme with SSL context
        if scheme in ("https", "http") and thrift_transport is None:
            port = port or 1000
            ssl_context = None
            if scheme == "https":
                from ssl import create_default_context  # noqa: PLC0415

                ssl_context = create_default_context()
                ssl_context.check_hostname = check_hostname == "true"
                ssl_cert = ssl_cert or "none"
                ssl_cert_parameter_map = {
                    "none": 0,
                    "optional": 1,
                    "required": 2,
                }
                ssl_context.verify_mode = ssl_cert_parameter_map.get(ssl_cert, 0)
            thrift_transport = thrift.transport.THttpClient.THttpClient(
                uri_or_host=f"{scheme}://{host}:{port}/cliservice/",
                ssl_context=ssl_context,
            )

            if auth in ("BASIC", "NOSASL", "NONE", None):
                self._set_authorization_header(thrift_transport, username, password)
            elif auth == "KERBEROS" and kerberos_service_name:
                self._set_kerberos_header(thrift_transport, kerberos_service_name, host)
            else:
                raise ValueError("Authentication is not valid use one of:BASIC, NOSASL, KERBEROS, NONE")
            host, port, auth, kerberos_service_name, password = (
                None,
                None,
                None,
                None,
                None,
            )

        username = username or getpass.getuser()
        configuration = configuration or {}

        if (password is not None) != (auth in ("LDAP", "CUSTOM")):
            raise ValueError(
                "Password should be set if and only if in LDAP or CUSTOM mode; "
                "Remove password or use one of those modes"
            )
        if (kerberos_service_name is not None) != (auth == "KERBEROS"):
            raise ValueError("kerberos_service_name should be set if and only if in KERBEROS mode")

        # Use puretransport if SSL is enabled or if thrift_transport is provided
        if use_ssl or thrift_transport is not None:
            if thrift_transport is not None:
                self._transport = thrift_transport
            else:
                import puretransport  # noqa: PLC0415

                socket_kwargs = {}
                if ssl_certfile:
                    socket_kwargs["certfile"] = ssl_certfile
                if ssl_keyfile:
                    socket_kwargs["keyfile"] = ssl_keyfile
                if ssl_ca_certs:
                    socket_kwargs["ca_certs"] = ssl_ca_certs
                if ssl_cert_reqs is not None:
                    socket_kwargs["cert_reqs"] = ssl_cert_reqs
                elif use_ssl:
                    socket_kwargs["cert_reqs"] = ssl.CERT_NONE

                self._transport = puretransport.transport_factory(
                    host=host or "localhost",
                    port=port or 10000,
                    username=username,
                    password=password or username,
                    use_ssl=use_ssl,
                    socket_kwargs=socket_kwargs if socket_kwargs else None,
                )
        else:
            if port is None:
                port = 10000
            if auth is None:
                auth = "NONE"
            socket = thrift.transport.TSocket.TSocket(host, port)
            if auth == "NOSASL":
                self._transport = thrift.transport.TTransport.TBufferedTransport(socket)
            elif auth in ("LDAP", "KERBEROS", "NONE", "CUSTOM"):
                import thrift_sasl  # noqa: PLC0415

                if auth == "KERBEROS":
                    sasl_auth = "GSSAPI"
                else:
                    sasl_auth = "PLAIN"
                    if password is None:
                        password = "x"

                self._transport = thrift_sasl.TSaslClientTransport(
                    lambda: get_installed_sasl(
                        host=host,
                        sasl_auth=sasl_auth,
                        service=kerberos_service_name,
                        username=username,
                        password=password,
                    ),
                    sasl_auth,
                    socket,
                )
            else:
                raise NotImplementedError(
                    f"Only NONE, NOSASL, LDAP, KERBEROS, CUSTOM authentication are supported, got {auth}"
                )

        protocol = thrift.protocol.TBinaryProtocol.TBinaryProtocol(self._transport)
        self._client = TCLIService.Client(protocol)
        protocol_version = ttypes.TProtocolVersion.HIVE_CLI_SERVICE_PROTOCOL_V6

        try:
            self._transport.open()
            open_session_req = ttypes.TOpenSessionReq(
                client_protocol=protocol_version,
                configuration=configuration,
                username=username,
            )
            response = self._client.OpenSession(open_session_req)
            _check_status(response)
            assert response.sessionHandle is not None, "Expected a session from OpenSession"
            self._sessionHandle = response.sessionHandle
            assert response.serverProtocolVersion == protocol_version, (
                f"Unable to handle protocol version {response.serverProtocolVersion}"
            )
            with contextlib.closing(self.cursor()) as cursor:
                cursor.execute(f"USE `{database}`")
        except:
            self._transport.close()
            raise
