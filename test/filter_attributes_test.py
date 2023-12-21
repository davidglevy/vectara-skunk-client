import unittest
import logging
from vectara.core import Factory
from vectara.domain import Corpus
from test.util import loadTestConfigAsJson
from dacite import from_dict

import json
import os

logging.basicConfig(
format='%(levelname)-5s:%(name)-35s:%(message)s', level=logging.INFO
)

class CorpusFilterAttributesIntTest(unittest.TestCase):

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.logger = logging.getLogger(__class__.__name__)
        self.test_corpus_name = __class__.__name__

    def setUp(self):
        self.logger.info("Loading Vectara Client")

        test_config_json = loadTestConfigAsJson("admin")

        factory = Factory(config_json=test_config_json)
        client = factory.build()

        self.admin_service = client.admin_service
        self.indexer_service = client.indexer_service

    def testWithFilterAttribute(self):
        # Split the test id by "." character, retrieve the last 2 parts (class/test-name) and rejoin with a hypen.
        # Then get the first 50 characters
        corpus_name = ("-".join(self.id().split(".")[2:]))[0:50]
        self.logger.info(f"We will run tests under corpus name [{corpus_name}]")

        # Check if exists.
        existing_corpora = self.admin_service.list_corpora(filter=corpus_name)

        if len(existing_corpora) == 1:
            self.logger.info(f"Deleting Existing Corpus [{self.test_corpus_name}]")
            self.admin_service.delete_corpus(existing_corpora[0].id)

        elif len(existing_corpora) > 1:
            raise Exception("Unexpected test issue - found multiple test corpora")

        attribute_dict = {"name": "category", "indexed": True, "type": "FILTER_ATTRIBUTE_TYPE__TEXT",
                          "level": "FILTER_ATTRIBUTE_LEVEL__DOCUMENT"}
        to_create = from_dict(Corpus, {"name": corpus_name, "filterAttributes": [attribute_dict]})

        create_corpus_response = self.admin_service.create_corpus(to_create)
        corpusId = create_corpus_response.corpusId

        ## Now lets upload the documents.
        doc_metadata = {"category": "blue"}
        path = os.sep.join([".", "resources", "sigmod_photon.pdf"])
        self.indexer_service.upload(corpusId, return_extracted=True, path=path, metadata=doc_metadata)

