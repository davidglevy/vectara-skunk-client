from vectara.client.domain import *
from typing import List, TypeVar
from vectara.client.util import RequestUtil, convertAttrListToDict
import logging

T = TypeVar("T")

class DocumentService():

    def __init__(self, request_util: RequestUtil):
        self.logger = logging.getLogger(__class__.__name__)
        self.request_util = request_util

    def list_documents(self, corpus_id: int, page: int = 0, page_size: int = 100,
                       metadata_filter: str = None) -> List[DocumentDTO]:

        payload = {"corpus_id": corpus_id, "page": page, "num_results": page_size}
        if metadata_filter:
            payload['metadata_filter'] = metadata_filter

        documents = []
        end_found = False

        page_key = None

        while not end_found:
            if page_key:
                payload['pageKey'] = page_key

            response = self.request_util.request("list-documents", payload, ListDocumentsResponse, method="POST")

            for doc in response.document:
                doc_id = doc.id
                if doc.metadata:
                    metadata = convertAttrListToDict(doc.metadata)
                else:
                    metadata = {}
                documents.append(DocumentDTO(doc_id, metadata))

            if response.nextPageKey:
                page_key = response.nextPageKey
            else:
                end_found = True

        return documents


