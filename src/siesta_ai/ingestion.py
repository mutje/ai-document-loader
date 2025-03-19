import logging
from siesta_ai.data_source_config import get_all_datasource_configs
from siesta_ai.parsing_handlers import parse_data_source
from langchain_community.vectorstores import FAISS  # Example vector store
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

def ingest_all():
    """Fetches data sources, parses them into documents, and ingests into vector store."""
    logging.info("Starting ingestion process...")
    configs = get_all_datasource_configs()

    for config in configs:
        if not config.enabled:
            logging.info(f"Skipping {config.source}, not enabled.")
            continue

        logging.info(f"Parsing and ingesting {config.source}...")

        # Parse data source into LangChain Document objects
        docs = parse_data_source(config)
        if docs:
            vector_store = FAISS.from_documents(docs, embedding=OpenAIEmbeddings())
            logging.info(f"Successfully ingested {len(docs)} documents from {config.source}.")
        else:
            logging.warning(f"No documents found for {config.source}.")

    logging.info("Ingestion completed!")

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    ingest_all()
