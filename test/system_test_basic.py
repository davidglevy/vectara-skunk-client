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


class AdminServiceIntegrationTest(unittest.TestCase):



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

        # Check existing corpus doesn't exist
        self.logger.info(f"Checking Corpus State [{self.test_corpus_name}]")
        corpora = self.admin_service.list_corpora(self.test_corpus_name)
        if len(corpora) == 1:
            self.logger.info(f"TODO: Deleting Existing Corpus [{self.test_corpus_name}]")
            self.admin_service.delete_corpus(corpora[0].id)

        elif len(corpora) > 1:
            raise Exception("Unexpected test issue - found multiple test corpora")


        self.logger.info(f"TODO Creating Corpora for System Test [{self.test_corpus_name}]")
        corpus = from_dict(Corpus, {'name': self.test_corpus_name, 'description': 'Test Corpus for system test. Delete after test.'})

        response = self.admin_service.create_corpus(corpus)
        self.logger.info(f"Created test corpus {response}")
        self.corpus_id = response.corpusId

    def _deleteTestCorpus(self):
        self.logger.info(f"Removing test corpus [{self.test_corpus_name}]")
        corpora = self.admin_service.list_corpora(self.test_corpus_name)
        if len(corpora) == 1:
            self.logger.info(f"Deleting Existing Corpus [{self.test_corpus_name}]")
            response = self.admin_service.delete_corpus(corpora[0].id)
            self.logger.info(f"Delete Corpus response [{response.code}]")
        elif len(corpora) > 1:
            raise Exception("Unexpected test issue - found multiple test corpora")

    def tearDown(self):
        if "testKeepCorpus" in os.environ:
            keep_corpus = bool(os.environ["testKeepCorpus"])
            if keep_corpus:
                self.logger.info("Flag set to retain test corpus")
            else:
                self._deleteTestCorpus()
        else:
            self._deleteTestCorpus()

    def testBasic(self):
        self.logger.info(f"Running Queries")

        path = os.sep.join([".", "resources", "sigmod_photon.pdf"])
        response = self.indexer_service.upload(self.corpus_id, path=path, return_extracted=True)

        #documents = self.admin_service.list_documents(self.corpus_id)

        print(response.response)



