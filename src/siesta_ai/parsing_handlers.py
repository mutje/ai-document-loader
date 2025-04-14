import logging
from langchain_community.document_loaders import (
    PyPDFLoader,
    ConfluenceLoader,
    GitbookLoader,
    RecursiveUrlLoader,
)
from siesta_ai.data_source_types import DataSourceType
from siesta_ai.data_source_config import DataSourceConfig

# Mapping DataSourceType → LangChain Loader
LOADER_MAPPING = {
    DataSourceType.PDF: PyPDFLoader, 
    DataSourceType.CONFLUENCE: ConfluenceLoader,
    DataSourceType.GITBOOK: GitbookLoader,
    DataSourceType.RECURSIVE_URL: RecursiveUrlLoader,
}

def parse_data_source(config: DataSourceConfig):
    """Dynamically selects and initializes the correct LangChain loader."""
    if config.source not in LOADER_MAPPING:
        raise ValueError(f"Unsupported data source: {config.source}")

    loader_class = LOADER_MAPPING[config.source]

    try:
        logging.info(f"Initializing loader for {config.source} with attributes: {config.attributes}")
        loader = loader_class(**config.attributes)
        docs = loader.load()
        logging.info(f"Successfully parsed {len(docs)} documents from {config.source}.")
        return docs
    except Exception as e:
        logging.error(f"Error parsing {config.source}: {str(e)}")
        return []
