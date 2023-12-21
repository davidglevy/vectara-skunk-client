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

class QueryService():

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