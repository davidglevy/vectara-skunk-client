import unittest
from test.base import BaseClientTest
from test.util import check_metadata

class BasicQuery(BaseClientTest):

    def setUp(self):
        super().setUp()
        self.upload_test_doc("./resources/research/D19-5819.pdf")

    def test_run_basic_query(self):
        """
        Basic test which runs a query and confirms that we receive back the correct document.
        :return:
        """
        resp = self.query_service.query("Are existing QA benchmarks sufficient for answering user "
                                        "questions at scale?", self.corpus_id, summary=False)

        self.assertTrue(len(resp.document) == 1)
        self.assertEqual(resp.document[0].id, 'D19-5819.pdf')
        expected_metadata = {'section': '5', 'offset': '318', 'len': '195'}
        check_metadata(self, expected_metadata, resp.response[0].metadata)

if __name__ == '__main__':
    unittest.main()
