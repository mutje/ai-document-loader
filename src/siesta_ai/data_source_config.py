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
    name: str
    source: DataSourceType
    attributes: dict[str, str]
    enabled: bool = True

def get_all_datasource_configs() -> list[DataSourceConfig]:
    return [
        DataSourceConfig(
            "ESG",
            DataSourceType.PDF, 
            {
                "file_path": "siesta_ai/ESG_Report_Skupiny_Letiste_Praha_za_rok_2023.pdf"
            }
        ),
        DataSourceConfig(
            "EXTRANET",
            DataSourceType.GITBOOK,
            {
                # TODO fix when langchain GitBook issue is fixed
                # See https://github.com/langchain-ai/langchain/issues/30473
                "web_page": "https://help.siestaextranet.com/obecne/untitled",
                "load_all_paths" :False, 
                # "web_page": "https://docs.gitbook.com/",
                # "load_all_paths" :True, 
            }
        )
    ]