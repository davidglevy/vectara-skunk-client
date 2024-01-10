import logging
import requests
import json
from dataclasses import asdict
from vectara.authn import BaseAuthUtil
from vectara.domain import *
from vectara.enums import ApiKeyStatus, ApiKeyType, ApiKeySort, SortDirection
from dacite import from_dict
from typing import Type, Any, List, TypeVar, overload, Union
from vectara.dao import CorpusDao
from vectara.status import StatusCode
from vectara.util import _custom_asdict_factory, RequestUtil

T = TypeVar("T")

class DocumentService():

    def __init__(self, request_util: RequestUtil):
        self.logger = logging.getLogger(__class__.__name__)
        self.request_util = request_util

    def list_documents(self, corpus_id: int, page: int = 0, page_size: int = 100,
                       metadata_filter: str = None) -> List[ListDocumentItem]:

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
            documents.extend(response.document)
            if response.nextPageKey:
                page_key = response.nextPageKey
            else:
                end_found = True

        return documents


