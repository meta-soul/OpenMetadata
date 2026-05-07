# Kyuubi

本节提供 Kyuubi 连接器的指南和参考。Kyuubi 使用 Spark 作为底层执行引擎，通过 HiveServer2 Thrift 协议进行通信。

## 要求
要提取元数据，连接中使用的用户需要能够在需要提取元数据的数据库/Schema 中执行 `SELECT`、`SHOW` 和 `DESCRIBE` 操作。

### Profiler & 数据质量
执行 Profiler 工作流或数据质量测试，需要用户在 Profiler/测试将要执行的表/Schema 上具有 `SELECT` 权限。有关 Profiler 工作流设置的更多信息，请参阅 <a href="https://docs.open-metadata.org/how-to-guides/data-quality-observability/profiler/workflow" target="_blank">此处</a>，数据质量测试请参阅 <a href="https://docs.open-metadata.org/connectors/ingestion/workflows/data-quality" target="_blank">此处</a>。

## Kyuubi 连接详情

$$section
### Scheme $(id="scheme")
SQLAlchemy driver scheme 选项。支持的选项有 `hive`（默认）、`hive+http` 和 `hive+https`。如果不确定此设置，可以使用默认值。
$$

$$section
### Username $(id="username")
连接 Kyuubi 的用户名。此用户应具有上述部分中描述的所需权限。
$$

$$section
### Password $(id="password")
连接 Kyuubi 的密码。
$$

$$section
### Host and Port $(id="hostPort")

此参数指定 Kyuubi 服务器的主机和端口。应指定为字符串格式 `hostname:port`。例如，可以将 hostPort 参数设置为 `mykyuubihost:10009`。

如果在 Docker 中运行 OpenMetadata 采集，且服务托管在 `localhost` 上，则使用 `host.docker.internal:10009` 作为值。
$$

$$section
### Authentication Mode $(id="auth")
auth 参数指定连接到 Kyuubi 服务器时使用的认证方法。可选值为 `NONE`（默认）、`LDAP`、`KERBEROS`、`CUSTOM`、`NOSASL`、`BASIC`、`GSSAPI`、`JWT` 和 `PLAIN`。
$$

$$section
### Kerberos Service Name $(id="kerberosServiceName")
此参数指定用于认证的 Kerberos 服务名称。仅在需要 Kerberos 认证时指定。
$$

$$section
### Database Schema $(id="databaseSchema")
数据源的 Schema。这是一个可选参数，如果希望将元数据读取限制在单个 Schema 中，可以指定。留空时，OpenMetadata 采集将尝试扫描所有 Schema。
$$

$$section
### Database Name $(id="databaseName")

在 OpenMetadata 中，Database 服务层次结构如下：
```
Database Service > Database > Schema > Table
```
对于 Kyuubi，我们通常没有 Database 这个概念。如果希望将数据放在一个不是 `default` 的数据库中，可以在此字段中指定数据库名称。
$$

$$section
### Auth Options $(id="authOptions")
传递给 Kyuubi 连接器的认证选项。这些选项基于 SQLAlchemy。
$$

$$section
### Use SSL $(id="useSSL")
启用与 Kyuubi 服务器的 SSL 连接。启用后，将使用 SSL 传输进行安全通信。
$$

### SSL Configuration
SSL 配置详情，包括 CA 证书、SSL 证书和用于客户端认证的 SSL 密钥。

### Connection Options
可以在连接期间发送给服务的额外连接选项，用于构建 URL。

### Connection Arguments
可以在连接期间发送给服务的额外连接参数，例如安全或协议配置。
