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
LakeInsight lineage module.

LakeInsight does not expose query log system tables, so lineage extraction
is not supported. This module provides a no-op lineage source that
can be used as a placeholder.
"""

from metadata.ingestion.source.database.lineage_source import LineageSource


class LakeInsightLineageSource(LineageSource):
    """
    No-op lineage source for LakeInsight.

    LakeInsight does not have query log system tables, so lineage extraction
    is not supported.
    """
