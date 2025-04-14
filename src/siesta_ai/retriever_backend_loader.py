import json
import re
from siesta_ai.key_vault_client import KeyVaultClient
from langchain_community.vectorstores.azuresearch import AzureSearch

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


def load_retriever_config(path: str) -> dict:
    with open(path) as f:
        config = json.load(f)

    kv = KeyVaultClient("kv-baiaia-dev")
    all_secrets = kv.get_all_app_settings()
    resolved = resolve_placeholders(config, all_secrets)

    return resolved["backends"][resolved["default"]]


def get_retriever_backend(embedding_function) -> AzureSearch:
    config = load_retriever_config()

    if config["type"] == "azure_search":
        return AzureSearch(
            azure_search_endpoint=config["endpoint"],
            azure_search_key=config["api_key"],
            index_name=config["index_name"],
            embedding_function=embedding_function
        )

    raise ValueError(f"Unsupported retriever type: {config['type']}")
