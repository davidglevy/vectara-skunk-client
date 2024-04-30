import unittest
from test.base import BaseClientTest


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

        resp1 = self.index_test_doc("./resources/temp/document.json", force=True)

