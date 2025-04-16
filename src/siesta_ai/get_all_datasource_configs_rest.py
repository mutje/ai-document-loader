import os
import requests
from siesta_ai.data_source_config import DataSourceConfig
from siesta_ai.data_source_types import DataSourceType

def get_all_datasource_configs() -> list[DataSourceConfig]:
    CONFIG_API_BASE = os.getenv("CONFIG_API_BASE")

    if not CONFIG_API_BASE:
        raise ValueError("CONFIG_API_BASE environment variable is not set.")

    try:
        response = requests.get(f"{CONFIG_API_BASE}/data_source")
        response.raise_for_status()
        configs = response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch data source configs: {e}")

    return [
        DataSourceConfig(
            config["name"],
            DataSourceType(str(config["source"]).lower()),
            config["attributes"]
        )
        for config in configs
    ]
