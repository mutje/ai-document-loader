import logging
from siesta_ai.key_vault_client import KeyVaultClient
from siesta_ai.data_source_config import get_all_datasource_configs
from siesta_ai.parsing_handlers import parse_data_source
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
import urllib
from langchain_core.documents import Document
from azure.identity import DefaultAzureCredential
import json

# new stuff
from azure.storage.blob import BlobServiceClient
AZURE_STORAGE_ACCOUNT_NAME = "stbaiaiadev" 
CONTAINER_NAME = "siesta-ai-experimental-container"

def load_all():
    """Processes documents, combines them into one JSON file, and uploads them to Azure Blob Storage."""
    logging.info("Starting loading process...")
    # kv = KeyVaultClient("kv-baiaia-dev")
    filename = "siesta_ai_experimental_docs.json"

    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net", credential=credential)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    all_docs = []  # Store all documents together

    blob_client = container_client.get_blob_client(blob=filename)

    configs = get_all_datasource_configs()

    for config in configs:
        if not config.enabled:
            logging.info(f"Skipping {config.source}, not enabled.")
            continue

        logging.info(f"Processing {config.source}...")

        try:
            docs = parse_data_source(config)
            if docs:
                all_docs.extend([
                    {
                        "id": doc.metadata.get("source", f"{config.source}_{i}"),  # Unique ID
                        "content": doc.page_content,
                        "metadata": doc.metadata
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
        doc_json = json.dumps(all_docs)
        blob_client.upload_blob(doc_json, overwrite=True)

        logging.info(f"Uploaded {len(all_docs)} documents to Azure Blob Storage ({filename}).")
    else:
        logging.warning("No documents to upload.")


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    load_all()

