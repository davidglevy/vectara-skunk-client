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


class SummaryError(Exception):

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

class QueryService():

    def __init__(self, request_util: RequestUtil, customer_id: int):
        self.logger = logging.getLogger(__class__.__name__)
        self.request_util = request_util
        self.customer_id = customer_id

    def query(self, query_text: str, corpus_id: int, start: int = 0, page_size: int = 10,
              summary: bool = True, response_lang:str='en'):
        corpus_key_dict = {'customerId': self.customer_id, 'corpusId': corpus_id}
        query_dict = {'query': query_text, 'numResults': page_size, 'corpusKey': [corpus_key_dict]}

        if summary:
            if response_lang:
                self.logger.info(f"Response Language set to [{response_lang}]")
            else:
                raise TypeError("If you are going to change from the default language (en) you must set one.")

            query_dict['summary'] = [{"summarizerPromptName": "vectara-summary-ext-v1.2.0",
                                      "responseLang": response_lang,
                                      "maxSummarizedResults": 5
                                      }]
        else:
            # Only put this in if we're not summarising.
            query_dict['start']: start

        batch_query_dict = {'query': [query_dict]}

        print(f"Query is:\n{json.dumps(batch_query_dict, indent=4)}\n")

        query = from_dict(BatchQueryRequest, batch_query_dict)

        # Omit nulls using our own dict factory.
        # Dataclasses feel like coding with the first XML serializers in Java in 2005 - very early.
        final_query_dict = asdict(query, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})

        result = self.request_util.request("query", final_query_dict, BatchQueryResponse)
        if len(result.status) > 0:
            # FIXME Talk to Tallat about this being empty and what it will look like when populated (OK)
            raise Exception(f"Unexpected response: {result.status}")
        elif summary and result.responseSet[0].summary[0].text.find("[1]") == 0:
            raise SummaryError("We did not have sufficient results")
        else:
            return result.responseSet[0]

