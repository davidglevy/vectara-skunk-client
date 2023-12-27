import logging
import requests
import json
from dataclasses import asdict
from vectara.authn import BaseAuthUtil
from vectara.domain import *
from dacite import from_dict
from typing import Type, Any, List, TypeVar
from vectara.dao import CorpusDao
from vectara.status import StatusCode
from vectara.util import _custom_asdict_factory, RequestUtil

T = TypeVar("T")

class AdminService():

    def __init__(self, request_util: RequestUtil, customer_id: int):
        self.logger = logging.getLogger(__class__.__name__)
        self.request_util = request_util
        self.customer_id = customer_id

    def list_corpora(self, filter: str = None, numResults: int = None, pageKey: int = None) -> List[Corpus]:
        payload = {}
        if filter:
            payload['filter'] = filter
        if numResults:
            payload['numResults'] = numResults
        if pageKey:
            payload['pageKey'] = pageKey

        response = self.request_util.request("list-corpora", payload, ListCorpusResponse)
        response.corpus.sort(key=lambda x: x.name)
        return response.corpus

    def read_corpus(self, corpus_id: int) -> CorpusInfo:
        request = ReadCorpusRequest([corpus_id], True, True, True, True, True, True)
        payload = asdict(request)
        response = self.request_util.request("read-corpus", payload, ReadCorpusResponse)
        # TODO Validate that there is 1 corpus and what happens if it doesn't exist.
        return response.corpora[0]

    def create_corpus(self, corpus: Corpus) -> CreateCorpusResponse:
        request = CreateCorpusRequest(corpus)
        payload = asdict(request, dict_factory=_custom_asdict_factory)
        response = self.request_util.request("create-corpus", payload, CreateCorpusResponse)
        if response.status.code == StatusCode.OK:
            self.logger.info(f"Created new corpus with {response.corpusId}")
            return response
        else:
            raise Exception(f"Unable to create corpus due to: {response.status}")

    def delete_corpus(self, corpus_id: int) -> Status:
        request = DeleteCorpusRequest(self.customer_id, corpus_id)
        payload = asdict(request)

        response = self.request_util.request("delete-corpus", asdict(request), DeleteCorpusResponse)
        return response.status

    def list_documents(self, corpus_id: int, page: int = 0, page_size: int = 100, metadata_filter: str=None) -> List[dict]:

        payload = {"corpus_id" : corpus_id, "page": page, "num_results": page_size}
        if metadata_filter:
            payload['metadata_filter'] = metadata_filter
        response = self.request_util.request("documents", payload, Any)
        return response.documents