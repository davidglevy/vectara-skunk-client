from vectara_client.core import Factory
from vectara_client.admin import CorpusBuilder
import unittest
import logging
import json

class CoreIndexTest(unittest.TestCase):

    def test_index_core_doc(self):
        logging.basicConfig(format='%(asctime)s:%(name)-35s %(levelname)s:%(message)s', level=logging.DEBUG,
                            datefmt='%H:%M:%S %z')

        logger = logging.getLogger(self.__class__.__name__)

        client = Factory().build()
        corpus = (CorpusBuilder("Core Document Test")
                  .add_attribute("author", "The author of the document", type="text")
                  .build())

        corpus_id = client.corpus_manager.create_corpus(corpus, delete_existing=True)

        metadata = {
            "author": "David Levy"
        }
        metadata_json = json.dumps(metadata)

        title_metadata = {
            "is_title": True
        }
        title_metadata_json = json.dumps(title_metadata)

        core_document = {
           "document_id": "test_core_doc_1",
           "metadata_json": metadata_json,
           "parts":  [
               {
                   "text": "The Giant Race",
                   "metadata_json": title_metadata_json
               },
               {
                   "text": "The giants decided to have a race. They would race over the castle and around the dragon."
               }
           ]
        }

        client.indexer_service.index_core_doc(corpus_id, core_document)

        doc = client.document_service.list_documents(corpus_id, metadata_filter="doc.id = 'test_core_doc_1'")[0]
        self.assertEqual(doc.id, "test_core_doc_1")
        self.assertEqual(doc.metadata["author"], "David Levy")

