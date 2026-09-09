# LakeInsight

In this section, we provide guides and references to use the LakeInsight connector. LakeInsight uses Spark as the underlying execution engine and communicates via the HiveServer2 Thrift protocol.

## Requirements
To extract metadata, the user used in the connection needs to be able to perform `SELECT`, `SHOW`, and `DESCRIBE` operations in the database/schema where the metadata needs to be extracted from.

### Profiler & Data Quality
Executing the profiler Workflow or data quality tests, will require the user to have `SELECT` permission on the tables/schemas where the profiler/tests will be executed. More information on the profiler workflow setup can be found <a href="https://docs.open-metadata.org/how-to-guides/data-quality-observability/profiler/workflow" target="_blank">here</a> and data quality tests <a href="https://docs.open-metadata.org/connectors/ingestion/workflows/data-quality" target="_blank">here</a>.

## LakeInsight Connection Details

$$section
### Scheme $(id="scheme")
SQLAlchemy driver scheme options. Supported options are `hive` (default), `hive+http`, and `hive+https`. If you are unsure about this setting, you can use the default value.
$$

$$section
### Username $(id="username")
Username to connect to LakeInsight. This user should have the necessary privileges described in the section above.
$$

$$section
### Password $(id="password")
Password to connect to LakeInsight.
$$

$$section
### Host and Port $(id="hostPort")

This parameter specifies the host and port of the LakeInsight server. This should be specified as a string in the format `hostname:port`. For example, you might set the hostPort parameter to `mylakeinsighthost:10009`.

If you are running the OpenMetadata ingestion in a docker and your services are hosted on the `localhost`, then use `host.docker.internal:10009` as the value.
$$

$$section
### Authentication Mode $(id="auth")
The auth parameter specifies the authentication method to use when connecting to the LakeInsight server. Possible values are `NONE` (default), `LDAP`, `KERBEROS`, `CUSTOM`, `NOSASL`, `BASIC`, `GSSAPI`, `JWT`, and `PLAIN`.
$$

$$section
### Kerberos Service Name $(id="kerberosServiceName")
This parameter specifies the Kerberos service name to use for authentication. This should only be specified if using Kerberos authentication.
$$

$$section
### Database Schema $(id="databaseSchema")
Schema of the data source. This is optional parameter, if you would like to restrict the metadata reading to a single schema. When left blank, OpenMetadata Ingestion attempts to scan all the schemas.
$$

$$section
### Database Name $(id="databaseName")

In OpenMetadata, the Database Service hierarchy works as follows:
```
Database Service > Database > Schema > Table
```
In the case of LakeInsight, we won't have a Database as such. If you'd like to see your data in a database named something other than `default`, you can specify the name in this field.
$$

$$section
### Auth Options $(id="authOptions")
Authentication options to pass to LakeInsight connector. These options are based on SQLAlchemy.
$$

$$section
### Use SSL $(id="useSSL")
Enable SSL connection to LakeInsight server. When enabled, SSL transport will be used for secure communication.
$$

### SSL Configuration
SSL Configuration details including CA certificate, SSL certificate, and SSL key for client authentication.

### Connection Options
Additional connection options to build the URL that can be sent to service during the connection.

### Connection Arguments
Additional connection arguments such as security or protocol configs that can be sent to service during connection.
