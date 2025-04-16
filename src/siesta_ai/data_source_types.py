from enum import StrEnum

class DataSourceType(StrEnum):
    PDF = "pdf"
    CONFLUENCE = "confluence"
    GITBOOK = "gitbook"
    RECURSIVE_URL = "recursive_url"
    ABP_DOCS = "abp_docs"
