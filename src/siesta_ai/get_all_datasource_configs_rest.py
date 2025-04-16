import os
import requests
from siesta_ai.data_source_config import DataSourceConfig
from siesta_ai.data_source_types import DataSourceType
from siesta_ai.api_config_loader import load_config_from_api

def get_all_datasource_configs() -> list[DataSourceConfig]:
    configs = load_config_from_api("data_source")
    return [
        DataSourceConfig(
            config["name"],
            DataSourceType(str(config["source"]).lower()),
            config["attributes"]
        )
        for config in configs
    ]