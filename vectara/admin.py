import logging
import requests
import json
from vectara.authn import BaseAuthUtil
from vectara.domain import ListCorpusResponse, Corpus
from dacite import from_dict
from typing import Type, Any, List


class AdminService():

    def __init__(self, auth_util: BaseAuthUtil):
        self.logger = logging.getLogger(__class__.__name__)
        self.auth_util = auth_util

    def _make_request(self, operation: str, payload: dict, to_class):
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

        response = requests.request("POST", url, headers=headers, data=payload)

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

        response = self._make_request("list-corpora", payload, ListCorpusResponse)

        response.corpus.sort(key=lambda x: x.name)

        return response.corpus
