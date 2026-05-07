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
Kyuubi source utility functions.

Kyuubi uses Spark as the underlying execution engine. The DESCRIBE TABLE
output format differs from Hive in how comments and detailed table info
are structured. These utilities adapt the Hive SQLAlchemy dialect methods
to handle Kyuubi's Spark-based output format.
"""

import re

from pyhive.sqlalchemy_hive import _type_map
from sqlalchemy import text, types, util
from sqlalchemy.engine import reflection

from metadata.ingestion.source.database.kyuubi.queries import KYUUBI_GET_TABLE_COMMENTS
from metadata.utils.logger import ingestion_logger

logger = ingestion_logger()

complex_data_types = ["struct", "map", "array", "union"]

_type_map.update(
    {
        "binary": types.BINARY,
        "char": types.CHAR,
        "varchar": types.VARCHAR,
        "decimal": types.DECIMAL,
    }
)


def get_columns(  # pylint: disable=unused-argument,too-many-locals
    self, connection, table_name, schema=None, **kw
):
    """
    Overrides HiveDialect.get_columns to handle Spark-based DESCRIBE TABLE output.

    Spark's DESCRIBE TABLE returns rows in the format (col_name, data_type, comment)
    but with different section markers than Hive. Kyuubi + Spark executes the DESCRIBE
    via the Hive Thrift protocol, so the raw result format is the same as Hive, but we
    need to handle the column rows properly.
    """
    rows = self._get_table_columns(connection, table_name, schema)  # pylint: disable=protected-access
    logger.info(f"Kyuubi get_columns: [{schema}.{table_name}] raw rows = {[list(r) for r in rows]}")
    rows = [[col.strip() if col else None for col in row] for row in rows]
    rows = [row for row in rows if row[0] and row[0] != "# col_name"]
    logger.info(f"Kyuubi get_columns: [{schema}.{table_name}] filtered rows = {rows}")
    result = []
    seen_columns = set()
    for col_name, raw_col_type, comment in rows:
        if col_name in ("# Partition Information", "# Partitioning"):
            break

        if col_name in seen_columns:
            continue

        attype = re.sub(r"\(.*\)", "", raw_col_type)
        col_type_name = re.search(r"^\w+", raw_col_type).group(0)
        try:
            coltype = _type_map[col_type_name]
        except KeyError:
            util.warn(f"Did not recognize type '{col_type_name}' of column '{col_name}'")
            coltype = types.NullType
        charlen = re.search(r"\(([\d,]+)\)", raw_col_type.lower())
        if charlen:
            charlen = charlen.group(1)
            if attype == "decimal":
                prec, scale = charlen.split(",")
                args = (int(prec), int(scale))
            elif attype.startswith("struct"):
                args = []
            else:
                args = (int(charlen),)
            coltype = coltype(*args)

        result.append(
            {
                "name": col_name,
                "type": coltype,
                "comment": comment,
                "nullable": True,
                "default": None,
                "system_data_type": raw_col_type,
                "is_complex": col_type_name in complex_data_types,
            }
        )
        seen_columns.add(col_name)
    return result


def get_table_names(  # pylint: disable=unused-argument
    self, connection, schema=None, **kw
):
    """
    Get table names from Kyuubi via Spark SQL.

    SHOW TABLES output format varies by Spark version:
    - Spark 3.x: 3 columns (namespace, tableName, isTemporary) -> row[1]
    - Spark 2.x: 2 columns (tableName, isTemporary) -> row[0]
    - Hive:      1 column  (tableName) -> row[0]
    """
    query = "SHOW TABLES"
    if schema:
        query += " IN " + self.identifier_preparer.quote_identifier(schema)
    logger.info(f"Kyuubi get_table_names: executing [{query}]")
    tables_in_schema = connection.execute(text(query))
    raw_rows = [list(row) for row in tables_in_schema]
    logger.info(f"Kyuubi get_table_names: raw rows = {raw_rows}")
    tables = []
    for row in raw_rows:
        if len(row) >= 3:
            tables.append(row[1])
        else:
            tables.append(row[0])
    logger.info(f"Kyuubi get_table_names: parsed tables = {tables}")
    return tables


def get_view_names(  # pylint: disable=unused-argument
    self, connection, schema=None, **kw
):
    return []


@reflection.cache
def get_table_comment(  # pylint: disable=unused-argument
    self, connection, table_name, schema_name, **kw
):
    """
    Returns comment of table.

    Kyuubi + Spark's DESCRIBE TABLE EXTENDED outputs the table comment in a
    different format from Hive. In Spark, the Comment is in the `col_name`
    column (first column) and the value is in the `data_type` column (second column),
    unlike Hive where the comment is in the `data_type` column.

    We check both formats for compatibility.
    """
    query = KYUUBI_GET_TABLE_COMMENTS.format(schema_name=schema_name, table_name=table_name)
    logger.info(f"Kyuubi get_table_comment: executing [{query}]")
    rows = connection.execute(text(query))
    try:
        for result in list(rows):
            data = result.values()
            logger.info(f"Kyuubi get_table_comment: [{schema_name}.{table_name}] raw row = {data}")
            if data[0] and data[0].strip().lower() == "comment":
                return {"text": data[1] if data and data[1] else None}
            if data[1] and data[1].strip() == "comment":
                return {"text": data[2] if data and data[2] else None}
    except Exception:
        return {"text": None}
    return {"text": None}


@reflection.cache
def get_view_definition(  # pylint: disable=unused-argument
    self, connection, view_name, schema=None, **kw
):
    """
    Gets the view definition from Kyuubi via Spark SQL.

    Spark SQL uses SHOW CREATE TABLE for both tables and views,
    which is compatible with this approach.
    """
    full_view_name = f"`{view_name}`" if not schema else f"`{schema}`.`{view_name}`"
    res = connection.execute(text(f"SHOW CREATE TABLE {full_view_name}")).fetchall()
    if res:
        return "\n".join(i[0] for i in res)
    return None
