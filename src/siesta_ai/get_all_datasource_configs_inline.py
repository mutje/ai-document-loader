from siesta_ai.data_source_config import DataSourceConfig
from siesta_ai.data_source_types import DataSourceType

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
                # "web_page": "https://help.siestaextranet.com/aplikace/aplikace/nastaveni/zdroje-rezervaci",
                # "load_all_paths" :False,
                "web_page": "https://help.siestaextranet.com/",
                "load_all_paths" :True, 
                "content_selector": "html"
            }
        ),
        # DataSourceConfig(
        #     "ABP_DOCS",
        #     DataSourceType.RECURSIVE_URL, 
        #     {
        #         "url": "https://abp.io/docs/latest/"
        #     }
        # ),
    ]