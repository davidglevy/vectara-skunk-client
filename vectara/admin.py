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
from vectara.util import _custom_asdict_factory

T = TypeVar("T")

class AdminService():

    def __init__(self, auth_util: BaseAuthUtil, customer_id: int):
        self.logger = logging.getLogger(__class__.__name__)
        self.auth_util = auth_util
        self.customer_id = customer_id


    def _make_request(self, operation: str, payload, to_class: Type[T], method="POST") -> T:
        """

        :param operation: the REST operation to perform.
        :param payload: the payload which will be serialized.
        :return:
        """
        headers = self.auth_util.get_headers()
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'

        self.logger.info(f"Headers: {json.dumps(headers)}")

        url = f"https://api.vectara.io/v1/{operation}"
        self.logger.info(f"URL for operation {operation} is: {url}")
        self.logger.info(f"Payload is: {json.dumps(payload)}")

        response = requests.request(method, url, headers=headers, data=payload)

        if response.status_code == 200:
            return from_dict(to_class, json.loads(response.text))
        else:
            self.logger.error(f"Received non 200 response {response.status_code}, throwing exception")
            response.raise_for_status()

    def list_corpora(self, filter: str = None, numResults: int = None, pageKey: int = None) -> List[Corpus]:
        payload = {}
        if filter:
            payload['filter'] = filter
        if numResults:
            payload['numResults'] = numResults
        if pageKey:
            payload['pageKey'] = pageKey

        response = self._make_request("list-corpora", json.dumps(payload), ListCorpusResponse)

        response.corpus.sort(key=lambda x: x.name)

        return response.corpus

    def read_corpus(self, corpus_id: int) -> CorpusInfo:
        request = ReadCorpusRequest([corpus_id], True, True, True, True, True, True)

        payload = json.dumps(asdict(request))

        response = self._make_request(f"read-corpus", payload, ReadCorpusResponse)

        return response.corpora[0]

    def create_corpus(self, corpus: Corpus) -> CreateCorpusResponse:
        request = CreateCorpusRequest(corpus)

        response = self._make_request("create-corpus", json.dumps(asdict(request, dict_factory=_custom_asdict_factory)), CreateCorpusResponse)
        if (response.status.code == StatusCode.OK):
            self.logger.info(f"Created new corpus with {response.corpusId}")
            return response
        else:
            raise Exception(f"Unable to create corpus due to: {response.status}")

    def delete_corpus(self, corpus_id: int) -> Status:
        request = DeleteCorpusRequest(self.customer_id, corpus_id)
        payload = json.dumps(asdict(request))

        response = self._make_request("delete-corpus", json.dumps(asdict(request)), DeleteCorpusResponse)
        return response.status

    def list_documents(self, corpus_id: int, page: int = 0, page_size: int = 100, metadata_filter: str=None) -> List[dict]:

        payload = {"corpus_id" : corpus_id, "page": page, "num_results": page_size}
        if metadata_filter:
            payload['metadata_filter'] = metadata_filter
        response = self._make_request("list-documents", json.dumps(payload), Any, method="GET")