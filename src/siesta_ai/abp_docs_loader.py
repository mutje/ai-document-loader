import requests
from langchain.schema import Document
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders.web_base import WebBaseLoader
import json
import re

class AbpDocsNavParser:
    def __init__(self, nav_url: str, base_url: str):
        self.nav_url = nav_url
        self.base_url = base_url

    def get_doc_urls(self) -> list[str]:
        nav_text = requests.get(self.nav_url).text.strip()
        nav_text = re.sub(r',(\s*[\]}])', r'\1', nav_text)  # removes trailing commas before ] or }
        nav_data = json.loads(nav_text)

        paths = self._extract_paths(nav_data["items"])
        return [f"{self.base_url}/{path}" for path in paths]

    def _extract_paths(self, items) -> list[str]:
        paths = []
        for item in items:
            if "items" in item:
                paths.extend(self._extract_paths(item["items"]))
            elif "path" in item:
                paths.append(item["path"])
        return paths

class AbpDocsLoader(BaseLoader):
    def __init__(self, nav_url: str, base_url: str):
        self.parser = AbpDocsNavParser(nav_url, base_url)

    def load(self) -> list[Document]:
        urls = self.parser.get_doc_urls()
        loader = WebBaseLoader(urls)
        return loader.load()
