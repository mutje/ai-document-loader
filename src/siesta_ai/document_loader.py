import logging
from siesta_ai.key_vault_client import KeyVaultClient
from siesta_ai.data_source_config import get_all_datasource_configs
from siesta_ai.parsing_handlers import parse_data_source
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
import urllib
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexerClient
import json
from azure.storage.blob import BlobServiceClient

AZURE_STORAGE_ACCOUNT_NAME = "stbaiaiadev" 
CONTAINER_NAME = "siesta-ai-experimental-container"
SEARCH_ENDPOINT = "https://cs-baiaia-dev.search.windows.net"
INDEXER_NAME = "indexer-siesta-ai-experimental"

def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return splitter.split_documents(docs)

def trigger_indexer(indexer_name: str):
    """Triggers an Azure Search indexer run."""

    indexer_client = SearchIndexerClient(
        endpoint=SEARCH_ENDPOINT,
        credential=DefaultAzureCredential()
    )

    print(f"Triggering indexer: {indexer_name}...")
    indexer_client.run_indexer(indexer_name)
    print("Indexer run triggered successfully.")


def load_all():
    """Processes documents, combines them into one JSON file, and uploads them to Azure Blob Storage."""
    logging.info("Starting loading process...")
    kv = KeyVaultClient("kv-baiaia-dev")
    filename = "siesta_ai_experimental_docs.json"

    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net", credential=credential)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    embeddings = OpenAIEmbeddings(api_key=kv.get_app_setting("OpenApiKey"))

    all_docs = [] 

    blob_client = container_client.get_blob_client(blob=filename)

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
            logging.info(f"Splitted to {len(docs)} chunks")

            docs_vectors = embeddings.embed_documents([doc.page_content for doc in docs])

            if docs:
                all_docs.extend([
                    {
                        "id": f"{config.name}_{i}",
                        "content": doc.page_content,
                        "metadata": json.dumps(doc.metadata),
                        "content_vector": docs_vectors[i]
                    }
                    for i, doc in enumerate(docs)
                ])
            else:
                logging.warning(f"No documents found for {config.source}.")
        except Exception as e:
            logging.error(f"Failed to process {config.source}: {str(e)}")

    if all_docs:
        blob_client = container_client.get_blob_client(blob=filename)

        # Convert to JSON and upload
        # all_docs = [] # TODO REMOVE KVIKLI
        doc_json = json.dumps(all_docs)
        blob_client.upload_blob(doc_json, overwrite=True)

        trigger_indexer(INDEXER_NAME)

        logging.info(f"Uploaded {len(all_docs)} documents to Azure Blob Storage ({filename}).")
    else:
        logging.warning("No documents to upload.")


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    load_all()
