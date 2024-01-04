import unittest
from vectara.domain import FilterAttribute, FilterAttributeType, FilterAttributeLevel, ResponseSet
from test.base import BaseClientTest
from test.util import check_metadata
from typing import List


class FilterAttributeTest(BaseClientTest):

    def _create_corpus_filter_attrs(self):
        attrs = super()._create_corpus_filter_attrs()
        customer_id_attr = FilterAttribute("customer_id", "Customers ID", True,
                                           FilterAttributeType.FILTER_ATTRIBUTE_TYPE__TEXT,
                                           FilterAttributeLevel.FILTER_ATTRIBUTE_LEVEL__DOCUMENT)
        current_attr = FilterAttribute("current", "Whether the document is still current", True,
                                       FilterAttributeType.FILTER_ATTRIBUTE_TYPE__BOOLEAN,
                                       FilterAttributeLevel.FILTER_ATTRIBUTE_LEVEL__DOCUMENT)
        attrs.extend([customer_id_attr, current_attr])
        return attrs

    def setUp(self):
        super().setUp()

    def check_doc_ids(self, response: ResponseSet, expected_doc_ids:List[str]):
        found_doc_ids = [doc.id for doc in response.document]
        found_doc_ids.sort()
        expected_doc_ids.sort()
        self.assertEqual(expected_doc_ids, found_doc_ids, f"We were expecting [{expected_doc_ids}] but received [{found_doc_ids}]")

    def test_filter_attr(self):
        """
        Runs multiple tests on metadata filter attributes.

        This test uses additional filters on the corpus:
        <ul>
          <li><em>customer_id:</em> example of a customer Id str</li>
          <li><em>current:</em> whether the record is current or archived - bool</li>
        </ul>

        :return:
        """
        self.index_test_doc("./resources/filter_attributes/document_1.json")
        self.index_test_doc("./resources/filter_attributes/document_2.json")
        self.index_test_doc("./resources/filter_attributes/document_3.json")

        qs = self.query_service

        # Test with only customer Id
        metadata_filter = "doc.customer_id = '1234'"
        response = qs.query("Evatt", self.corpus_id, summary=False, metadata=metadata_filter)
        self.check_doc_ids(response, ["doc-id-1", "doc-id-2"])

        # Test with customer 1234 and current.
        metadata_filter = "doc.customer_id = '1234' and doc.current"
        response = qs.query("Evatt", self.corpus_id, summary=False, metadata=metadata_filter)
        self.check_doc_ids(response, ["doc-id-1"])

        # Test with unknown customer Id (not in corpus)
        metadata_filter = "doc.customer_id = '9999'"
        response = qs.query("Evatt", self.corpus_id, summary=False, metadata=metadata_filter)
        self.check_doc_ids(response, [])

        # Test with only current.
        metadata_filter = "not doc.current"
        response = qs.query("Evatt", self.corpus_id, summary=False, metadata=metadata_filter)
        self.check_doc_ids(response, ["doc-id-2"])






if __name__ == '__main__':
    unittest.main()
