#  Copyright 2021 Collate
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""
This script generates the Python models from the JSON Schemas definition. Additionally, it replaces the `SecretStr`
pydantic class used for the password fields with the `CustomSecretStr` pydantic class which retrieves the secrets
from a configured secrets' manager.
"""
import datamodel_code_generator.model.pydantic
from datamodel_code_generator.imports import Import
import os
import re


datamodel_code_generator.model.pydantic.types.IMPORT_SECRET_STR = Import.from_full_path(
    "metadata.ingestion.models.custom_pydantic.CustomSecretStr"
)

from datamodel_code_generator.__main__ import main

current_directory = os.getcwd()
ingestion_path = "./" if current_directory.endswith("/ingestion") else "ingestion/"
directory_root = "../" if current_directory.endswith("/ingestion") else "./"

UTF_8 = "UTF-8"
UNICODE_REGEX_REPLACEMENT_FILE_PATHS = [
    f"{ingestion_path}src/metadata/generated/schema/entity/classification/tag.py",
    f"{ingestion_path}src/metadata/generated/schema/entity/events/webhook.py",
    f"{ingestion_path}src/metadata/generated/schema/entity/teams/user.py",
    f"{ingestion_path}src/metadata/generated/schema/entity/type.py",
    f"{ingestion_path}src/metadata/generated/schema/type/basic.py",
]

args = f"--input {directory_root}openmetadata-spec/src/main/resources/json/schema --output-model-type pydantic_v2.BaseModel --use-annotated --base-class metadata.ingestion.models.custom_pydantic.BaseModel --input-file-type jsonschema --output {ingestion_path}src/metadata/generated/schema --set-default-enum-member".split(" ")

main(args)

for file_path in UNICODE_REGEX_REPLACEMENT_FILE_PATHS:
    with open(file_path, "r", encoding=UTF_8) as file_:
        content = file_.read()
        # Python now requires to move the global flags at the very start of the expression
        content = content.replace("(?U)", "(?u)")
    with open(file_path, "w", encoding=UTF_8) as file_:
        file_.write(content)

# Until https://github.com/koxudaxi/datamodel-code-generator/issues/1895
# TODO: This has been merged but `Union` is still not there. We'll need to validate
MISSING_IMPORTS = [f"{ingestion_path}src/metadata/generated/schema/entity/applications/app.py",]
WRITE_AFTER = "from __future__ import annotations"

for file_path in MISSING_IMPORTS:
    with open(file_path, "r", encoding=UTF_8) as file_:
        lines = file_.readlines()
    with open(file_path, "w", encoding=UTF_8) as file_:
        for line in lines:
            file_.write(line)
            if line.strip() == WRITE_AFTER:
                file_.write("from typing import Union  # custom generate import\n\n")


# unsupported rust regex pattern for pydantic v2
# https://docs.pydantic.dev/2.7/api/config/#pydantic.config.ConfigDict.regex_engine
# We'll remove validation from the client and let it fail on the server, rather than on the model generation
UNSUPPORTED_REGEX_PATTERN_FILE_PATHS = [
    f"{ingestion_path}src/metadata/generated/schema/type/basic.py",
    f"{ingestion_path}src/metadata/generated/schema/entity/data/searchIndex.py",
    f"{ingestion_path}src/metadata/generated/schema/entity/data/table.py",
]

for file_path in UNSUPPORTED_REGEX_PATTERN_FILE_PATHS:
    with open(file_path, "r", encoding=UTF_8) as file_:
        content = file_.read()
        content = content.replace("pattern='^((?!::).)*$',", "")
    with open(file_path, "w", encoding=UTF_8) as file_:
        file_.write(content)

# Until https://github.com/koxudaxi/datamodel-code-generator/issues/1996
# Supporting timezone aware datetime is too complex for the profiler
DATETIME_AWARE_FILE_PATHS = [
    f"{ingestion_path}src/metadata/generated/schema/type/basic.py",
]

for file_path in DATETIME_AWARE_FILE_PATHS:
    with open(file_path, "r", encoding=UTF_8) as file_:
        content = file_.read()
        content = content.replace(
            "from pydantic import AnyUrl, AwareDatetime, ConfigDict, EmailStr, Field, RootModel",
            "from pydantic import AnyUrl, ConfigDict, EmailStr, Field, RootModel"
        )
        content = content.replace("from datetime import date, time", "from datetime import date, time, datetime")
        content = content.replace("AwareDatetime", "datetime")
    with open(file_path, "w", encoding=UTF_8) as file_:
        file_.write(content)

# Field names that match an imported module (e.g. `votes: Optional[votes.Votes]`)
# shadow that module in the class namespace. On Python 3.10 (Airflow image), pydantic
# forward-ref evaluation then fails with:
#   AttributeError: 'NoneType' object has no attribute 'Votes'
# Alias conflicting imports to `{name}Module` after codegen.
def _fix_import_module_field_shadowing(schema_root: str) -> None:
    import_block_re = re.compile(r"(from\s+\S+\s+import\s+\()(.*?)(\))", re.S)
    import_single_re = re.compile(r"^(from\s+\S+\s+import\s+)([^(].*?)$", re.M)
    field_re = re.compile(r"^\s{4}([A-Za-z_][A-Za-z0-9_]*):", re.M)
    imported_name_re = re.compile(
        r"([A-Za-z_][A-Za-z0-9_]*)(?:\s+as\s+([A-Za-z_][A-Za-z0-9_]*))?"
    )

    def _collect_imported_names(content: str) -> set:
        imported = set()
        for _, body, _ in import_block_re.findall(content):
            for part in body.split(","):
                match = imported_name_re.match(part.strip())
                if match:
                    imported.add(match.group(2) or match.group(1))
        for _, body in import_single_re.findall(content):
            for part in body.split(","):
                match = imported_name_re.match(part.strip())
                if match:
                    imported.add(match.group(2) or match.group(1))
        return imported

    for root, _, files in os.walk(schema_root):
        for filename in files:
            if not filename.endswith(".py"):
                continue
            file_path = os.path.join(root, filename)
            with open(file_path, "r", encoding=UTF_8) as file_:
                content = file_.read()

            fields = set(field_re.findall(content))
            conflicts = sorted(
                name
                for name in _collect_imported_names(content)
                if not name.endswith("Module")
                and name in fields
                and re.search(rf"\b{name}\.[A-Za-z_]", content)
            )
            if not conflicts:
                continue

            updated = content
            for name in sorted(conflicts, key=len, reverse=True):
                alias = f"{name}Module"

                def _alias_block(body: str, _name: str = name, _alias: str = alias) -> str:
                    return re.sub(
                        rf"(?m)^([ \t]*){_name}([ \t]*,?[ \t]*)$",
                        rf"\1{_name} as {_alias}\2",
                        body,
                    )

                def _sub_blocks(match: re.Match) -> str:
                    return match.group(1) + _alias_block(match.group(2)) + match.group(3)

                def _sub_single(match: re.Match, _name: str = name, _alias: str = alias) -> str:
                    prefix, body = match.group(1), match.group(2)
                    parts = []
                    for part in body.split(","):
                        stripped = part.strip()
                        name_match = imported_name_re.match(stripped)
                        if (
                            name_match
                            and name_match.group(1) == _name
                            and not name_match.group(2)
                        ):
                            leading = re.match(r"^(\s*)", part).group(1)
                            trailing = re.search(r"(\s*)$", part).group(1)
                            parts.append(f"{leading}{_name} as {_alias}{trailing}")
                        else:
                            parts.append(part)
                    return prefix + ",".join(parts)

                updated = import_block_re.sub(_sub_blocks, updated)
                updated = import_single_re.sub(_sub_single, updated)
                updated = re.sub(
                    rf"\b{name}\.([A-Za-z_][A-Za-z0-9_]*)",
                    rf"{alias}.\1",
                    updated,
                )

            if updated != content:
                with open(file_path, "w", encoding=UTF_8) as file_:
                    file_.write(updated)


_fix_import_module_field_shadowing(f"{ingestion_path}src/metadata/generated/schema")
