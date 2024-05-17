from vectara_client.core import Factory
from vectara_client.domain import Corpus
from vectara_client.corpus import CorpusManager
from vectara_client.admin import CorpusBuilder
from typing import Union
from datetime import datetime
import unittest
import logging

import os

logging.basicConfig(
format='%(levelname)-5s:%(name)-35s:%(message)s', level=logging.INFO
)
logging.getLogger("OAuthUtil").setLevel(logging.WARNING)

class CorpusManagerTest(unittest.TestCase):

    CORPUS_NAME = "test-corpus-manager"

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.logger = logging.getLogger(__class__.__name__)
        self.test_corpus_name = __class__.__name__
        self.client = Factory().build()


    def setUp(self):
        super().setUp()
        manager = self.client.corpus_manager
        manager.delete_corpus_by_name(self.CORPUS_NAME)

    def test_script(self):
        corpus = (CorpusBuilder(self.CORPUS_NAME).description("Test CorpusManager functions").build())

        manager = self.client.corpus_manager
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

    def test_corpus_delete_recreate(self):
        manager = self.client.corpus_manager
        corpus_ids = manager.find_corpus_by_name(self.CORPUS_NAME, fail_if_not_exist=False)
        self.assertIsNone(corpus_ids)

        corpus = (CorpusBuilder(self.CORPUS_NAME).description("Test CorpusManager functions").build())
        corpus_id = manager.create_corpus(corpus, delete_existing=True)

        found_corpus_id = manager.find_corpus_by_name(self.CORPUS_NAME)
        self.assertEqual(corpus_id, found_corpus_id)


    def test_batch_index(self):
        corpus = (CorpusBuilder(self.CORPUS_NAME).description("Test CorpusManager functions").build())

        manager = self.client.corpus_manager
        corpus_id = manager.create_corpus(corpus)

        documents = []

        # Increase this for "bigger" test.
        for x in range(20):
            document = {
                "document_id": "doc-" + str(x),
                "title": f"This is document number {x}",
                "section": [
                    {"text": "Cool document"}
                ]
            }
            documents.append(document)


        # Uncomment this for a higher stress test.
        #thread_counts = [1, 2, 5, 10, 20, 50]
        thread_counts = [1, 2, 5, 10]

        times = []

        for thread_count in thread_counts:
            tick = datetime.now()

            # run the tests here
            # First test with 1
            manager.batch_index(corpus_id, documents, threads=thread_count)
            tock = datetime.now()
            diff = tock - tick  # the result is a datetime.timedelta object
            difference_ms = int(diff.total_seconds() * 1000)
            times.append({"thread_count": thread_count, "time_ms": difference_ms})

        last_time: Union[None, int] = None
        for time in times:
            current_time = time['time_ms']
            thread_count = time['thread_count']
            self.logger.info(f"For thread count of [{thread_count}], time taken was [{current_time}] milliseconds")
            if last_time:
                self.assertGreater(last_time, current_time)
            last_time = current_time








