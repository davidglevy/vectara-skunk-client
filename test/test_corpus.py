import unittest
import logging
from vectara_client.core import Factory
from vectara_client.domain import Corpus
from vectara_client.corpus import CorpusManager
from vectara_client.admin import CorpusBuilder

import os

logging.basicConfig(
format='%(levelname)-5s:%(name)-35s:%(message)s', level=logging.INFO
)

class CorpusManagerTest(unittest.TestCase):

    CORPUS_NAME = "test-corpus-manager"

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.logger = logging.getLogger(__class__.__name__)
        self.test_corpus_name = __class__.__name__

    def setUp(self):
        super().setUp()
        client = Factory().build()
        manager = client.corpus_manager
        manager.delete_corpus_by_name(self.CORPUS_NAME)

    def test_script(self):
        client = Factory().build()

        corpus = (CorpusBuilder(self.CORPUS_NAME).description("Test CorpusManager functions").build())

        manager = client.corpus_manager
        corpus_id = manager.create_corpus(corpus)

        # Check that we get a failure if we try create a corpus with same name.
        with self.assertRaises(Exception) as cm:
            manager.create_corpus(corpus)

        message = str(cm.exception)
        self.assertIn(f"Unable to create a corpus with the name [{corpus.name}] as there were existing ones and "
                                f"the flag \"delete_existing\" is \"False\".", message)

        # Check that it works if we specify delete_existing = True
        new_corpus_id = manager.create_corpus(corpus, delete_existing=True)
        self.assertNotEqual(corpus_id, new_corpus_id, "We should have received a new corpus id")

        # This test verifies that there is a single corpus found with the given name and it matches the second id.
        found_corpus_id = manager.find_corpus_by_name(self.CORPUS_NAME)
        self.assertEqual(found_corpus_id, new_corpus_id)





