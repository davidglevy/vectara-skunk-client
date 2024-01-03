import unittest
from vectara.domain import FilterAttribute, FilterAttributeType, FilterAttributeLevel
from test.base import BaseClientTest
from test.util import check_metadata


class FilterAttributes(BaseClientTest):

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


    def test_index_doc(self):
        """
        Basic test which indexes a document
        :return:
        """
        self.index_test_doc("./resources/filter_attributes/document_1.json")
        self.index_test_doc("./resources/filter_attributes/document_2.json")
        self.index_test_doc("./resources/filter_attributes/document_3.json")

if __name__ == '__main__':
    unittest.main()
