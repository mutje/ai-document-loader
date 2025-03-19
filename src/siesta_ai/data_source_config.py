'''
This file reads DataSourceConfig to know which sources to ingest.

Right now it is fake generator, 
but later can be edited to fetch from database, 
filter by individual 
'''

from siesta_ai.data_source_types import DataSourceType
from dataclasses import dataclass

@dataclass
class DataSourceConfig:
    source: DataSourceType
    attributes: dict[str, str]
    enabled: bool = True

def get_all_datasource_configs() -> list[DataSourceConfig]:
    return [
        DataSourceConfig(
            DataSourceType.PDF, 
            {
                "file_path": "siesta_ai/hantec.pdf"
            }
        )
    ]