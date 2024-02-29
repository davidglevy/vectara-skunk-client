import json
from dataclasses import asdict
from vectara_client.domain import *
from dacite import from_dict
from typing import List, TypeVar, Union
from vectara_client.status import StatusCode
from vectara_client.util import _custom_asdict_factory, RequestUtil
import logging
import re

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

    def query(self, query_text: str, corpus_id: Union[int, List[int]], start: int = 0, page_size: int = 10,
              summary: bool = True, response_lang: str = 'en', context_config=None, semantics='DEFAULT',
              promptText=None, metadata: str = None, summarizer: str = "vectara-summary-ext-v1.2.0",
              summary_result_count=5, re_rank=False, custom_dimensions:List[dict]=None, _lambda=0.025,
              temperature=None):

        # Convert singular int to List of corpus ids.
        if type(corpus_id) is list:
            corpus_ids = corpus_id
        else:
            corpus_ids = [corpus_id]

        if not context_config:
            context_config = {
                'charsBefore': 30,
                'charsAfter': 30,
                'sentencesBefore': 2,  # Change to align with UI to 2
                'sentencesAfter': 2,
                'startTag': '<b>',
                'endTag': '</b>'
            }

        corpus_keys = []
        for id in corpus_ids:
            corpus_key = {'customerId': self.customer_id,
                          'corpusId': id,
                          'semantics': semantics
                          }
            if metadata:
                corpus_key['metadataFilter'] = metadata

            if custom_dimensions:
                corpus_key['dim'] = custom_dimensions

            corpus_keys.append(corpus_key)

        query_dict = {
            'query': query_text,
            'numResults': page_size,
            'contextConfig': context_config,
            'corpusKey': corpus_keys
        }

        if re_rank:
            query_dict['rerankingConfig'] = {
                "rerankerId": 272725718,
                "mmrConfig": {
                    "diversityBias": 0.3
                }
            }

        if summary:
            if response_lang:
                self.logger.debug(f"Response Language set to [{response_lang}]")
            else:
                raise TypeError("If you are going to change from the default language (en) you must set one.")

            # Old: vectara-summary-ext-v1.2.0
            # New: vectara-summary-ext-v1.3.0
            query_dict['summary'] = [{"summarizerPromptName": summarizer,
                                      "responseLang": response_lang,
                                      "maxSummarizedResults": summary_result_count
                                      }]
            if promptText:
                query_dict['summary'][0]['promptText'] = promptText

            if temperature:
                query_dict['summary'][0]['model_params'] = {'temperature': temperature}
        else:
            # Only put this in if we're not summarising.
            query_dict['start']: start



        batch_query_dict = {'query': [query_dict]}

        self.logger.debug(f"Query is:\n{json.dumps(batch_query_dict, indent=4)}\n")

        query = from_dict(BatchQueryRequest, batch_query_dict)

        # Omit nulls using our own dict factory.
        # Dataclasses feel like coding with the first XML serializers in Java in 2005 - very early.
        final_query_dict = asdict(query, dict_factory=_custom_asdict_factory)

        # Since we can't put in "lambda" to a dataclass field due to Python using it as a reserved word,
        # we inject it now.
        final_query_dict['query'][0]['corpusKey'][0]['lexicalInterpolationConfig'] = {"lambda": _lambda}

        result = self.request_util.request("query", final_query_dict, BatchQueryResponse)

        summary_status = None
        if summary:
            if (result.responseSet[0].summary[0].status and result.responseSet[0].summary[0].status
                    and len(result.responseSet[0].summary[0].status and result.responseSet[0].summary[0].status) > 0):
                # TODO Ask Tallat on Status for summary (why List)
                # No idea if it's possible to have more than one status
                summary_status = result.responseSet[0].summary[0].status[0]

        if summary_status and summary_status.code != StatusCode.OK:
            raise SummaryError(f"Unable to generate summary due to: {summary_status}")

        if len(result.status) > 0:
            # FIXME Talk to Tallat about this being empty and what it will look like when populated (OK)
            raise Exception(f"Unexpected response: {result.status}")
        elif summary and not re.search(r"\[[0-9]+\]", result.responseSet[0].summary[0].text):
            status = Status("INVALID_ARGUMENT", None, None)

            result.responseSet[0].summary[0].status = status
            return result.responseSet[0]
            # raise SummaryError("We did not have sufficient results to generate results.")
        else:
            return result.responseSet[0]
