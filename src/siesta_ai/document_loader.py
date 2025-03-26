import logging
import os
import tempfile
import json

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.indexes import SQLRecordManager, index
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_core.documents import Document

from siesta_ai.key_vault_client import KeyVaultClient
from siesta_ai.data_source_config import get_all_datasource_configs
from siesta_ai.parsing_handlers import parse_data_source


AZURE_STORAGE_ACCOUNT_NAME = "stbaiaiadev"
CONTAINER_NAME = "siesta-ai-experimental-container"
SQLITE_BLOB_NAME = "langchain_record_manager.db"
LOCAL_SQLITE_PATH = "/tmp/langchain_record_manager.db"  # Used inside Azure Function
SEARCH_ENDPOINT = "https://cs-baiaia-dev.search.windows.net"
SEARCH_INDEX_NAME = "csindex-siesta-ai-experimental"

def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return splitter.split_documents(docs)

def load_all():
    logging.info("Starting indexing process...")

    kv = KeyVaultClient("kv-baiaia-dev")
    credential = DefaultAzureCredential()

    # Azure Blob setup
    blob_service_client = BlobServiceClient(account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net", credential=credential)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blob_client = container_client.get_blob_client(SQLITE_BLOB_NAME)

    # Download SQLite DB blob (if exists)
    try:
        with open(LOCAL_SQLITE_PATH, "wb") as f:
            f.write(blob_client.download_blob().readall())
        logging.info("Downloaded existing SQLite DB from blob.")
    except Exception:
        logging.info("No existing SQLite DB found, starting fresh.")

    # Set up LangChain components
    embeddings = OpenAIEmbeddings(api_key=kv.get_app_setting("OpenApiKey"))
    record_manager = SQLRecordManager(db_url=f"sqlite:///{LOCAL_SQLITE_PATH}", namespace="siesta-ai-index")
    record_manager.create_schema()

    vectorstore = AzureSearch(
        azure_search_endpoint=SEARCH_ENDPOINT,
        azure_search_key=kv.get_app_setting("SearchServiceApiKey"),
        index_name=SEARCH_INDEX_NAME,
        embedding_function=embeddings
    )

    all_docs = []

    # Load and parse sources
    configs = get_all_datasource_configs()

    for config in configs:
        if not config.enabled:
            logging.info(f"Skipping {config.source}, not enabled.")
            continue

        logging.info(f"Processing {config.source}...")
        try:
            docs = parse_data_source(config)
            logging.info(f"Splitting {len(docs)} docs")
            docs = split_docs(docs)
            logging.info(f"Split into {len(docs)} chunks")

            all_docs.extend(docs)
        except Exception as e:
            logging.error(f"Failed to process {config.source}: {str(e)}")

    # LangChain indexing
    logging.info("Starting LangChain indexing...")

    ir = index(
        all_docs,
        record_manager,
        vectorstore,
        cleanup="full",
        source_id_key="source")
    logging.info(f"Indexed {len(all_docs)} documents.")
    logging.info(ir)

    # Upload SQLite DB back to Blob
    with open(LOCAL_SQLITE_PATH, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    logging.info("Uploaded updated SQLite DB to blob.")


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    load_all()
