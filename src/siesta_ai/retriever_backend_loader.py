import json
import re
from siesta_ai.key_vault_client import KeyVaultClient
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_sqlserver import SQLServer_VectorStore

from azure.search.documents.indexes.models import (
    ScoringProfile,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    TextWeights,
)

def resolve_placeholders(obj: str|list|dict, secret_client: KeyVaultClient):
    pattern = re.compile(r"{{(.*?)}}")

    if isinstance(obj, dict):
        return {k: resolve_placeholders(v, secret_client) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_placeholders(i, secret_client) for i in obj]
    elif isinstance(obj, str):
        match = pattern.fullmatch(obj.strip())
        if match:
            key = match.group(1)
            return secret_client.get_app_setting(key)
    return obj


def load_retriever_config() -> dict:
    # with open(path) as f:
    #     config = json.load(f)

    # Hardcoded now, experimenting
    config = {
        "default": "azure_search",
        "backends": {
            "azure_search": {
                "type": "azure_search",
                "endpoint": "https://cs-baiaia-dev.search.windows.net",
                "index_name": "csindex-siesta-ai-experimental",
                "api_key": "{{SearchServiceApiKey}}"
            },
            "azure_sql": {
                "type": "azure_sql",
                "connection_string": "{{AzureSqlConnectionString}}",
                "table_name": "documents",
                "embedding_length": 1536
            }
        }
    }

    kv = KeyVaultClient("kv-baiaia-dev")
    resolved = resolve_placeholders(config, kv)

    return resolved["backends"][resolved["default"]]


def get_retriever_backend(embedding_function) -> AzureSearch:
    config = load_retriever_config()

    if config["type"] == "azure_search":
        return AzureSearch(
            azure_search_endpoint=config["endpoint"],
            azure_search_key=config["api_key"],
            index_name=config["index_name"],
            embedding_function=embedding_function,
            fields = [
                SimpleField(
                    name="id",
                    type=SearchFieldDataType.String,
                    key=True,
                    filterable=True,
                ),
                SearchableField(
                    name="content",
                    type=SearchFieldDataType.String,
                    searchable=True,
                ),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="myHnswProfile",
                ),
                SearchableField(
                    name="metadata",
                    type=SearchFieldDataType.String,
                    searchable=True,
                ),
                SimpleField(
                    name="data_source_id",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
            ]
        )

    elif config["type"] == "azure_sql":
        return SQLServer_VectorStore(
            connection_string=config["connection_string"],
            table_name=config["table_name"],
            embedding_function=embedding_function,
            embedding_length=config["embedding_length"]
        )

    raise ValueError(f"Unsupported retriever type: {config['type']}")
