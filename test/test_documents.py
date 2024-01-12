import unittest
from vectara.util import MarkdownFormatter, render_markdown_req
from test.base import BaseClientTest
from test.util import check_metadata
import json

class BasicQuery(BaseClientTest):

    def setUp(self):
        super().setUp()

    def test_documents_info(self):
        """
        Test Document List Test.
        :return:
        """

        dict1 = {"owner": "david"}
        dict2 = {"owner": "justin"}

        #resp1 = self.index_test_doc("./resources/filter_attributes/document_1.json", force=True)
        #resp2 = self.index_test_doc("./resources/filter_attributes/document_2.json", force=True)
        #resp3 = self.index_test_doc("./resources/filter_attributes/document_3.json", force=True)

        doc_service = self.client.document_service

        doc_list = doc_service.list_documents(self.corpus_id)
        for doc in doc_list:
            self.logger.info(f"We found [{doc}]")

        # TODO Assert metadata returned.

        doc_list = doc_service.list_documents(self.corpus_id, page_size=2)
        self.assertEqual(3, len(doc_list))


        # Test Metadata filter
        doc_list = doc_service.list_documents(self.corpus_id, metadata_filter="doc.id = 'doc-id-1'")
        self.assertEqual(1, len(doc_list))
        self.assertEqual("doc-id-1", doc_list[0].id)
        self.assertEqual("e01c8b476dc7b4ef6457777ccd09bd75f43e390c", doc_list[0].metadata['sha1_hash'])



if __name__ == '__main__':
    unittest.main()
