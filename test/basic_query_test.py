import unittest
from vectara_client.util import MarkdownFormatter, render_markdown
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

        last_request = self.client.get_requests()[-1]
        self.logger.info(f"Last request was of type [{last_request['operation']}]")

        formatter = MarkdownFormatter()

        formatted_request = render_markdown_req(last_request)
        self.logger.info(f"Markdown formatted request:\n{formatted_request}")

    def test_basic_summary(self):
            """
            Basic test which runs a query and confirms that we can generate a summary.
            :return:
            """
            query = "Are existing QA benchmarks sufficient for answering user questions at scale?"
            resp = self.query_service.query(query, self.corpus_id, summary=True)
            formatted_request = render_markdown(query, resp)
            self.logger.info(f"Markdown formatted request:\n{formatted_request}")

if __name__ == '__main__':
    unittest.main()
