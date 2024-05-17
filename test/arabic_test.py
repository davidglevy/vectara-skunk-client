from test.base import BaseClientTest
from vectara_client.util import render_markdown, _custom_asdict_factory
from dataclasses import asdict
import json

class TestArabic(BaseClientTest):

    def setUp(self):
        super().setUp()
        self.upload_test_doc("./resources/ksa/gem-ksa-national-report-20222023-ar-digital-final.pdf")

    def test_arabic_with_summary_gpt4(self):
        qs = self.query_service

        query = "Is it important to develop the Kingdom’s economy by increasing employment opportunities?"
        resp = qs.query(query, self.corpus_id, summarizer="vectara-summary-ext-v1.3.0")

        self.logger.info(render_markdown(query, resp))

    def test_arabic_with_summary_gpt4_resp_ar(self):
        qs = self.query_service

        query = "Is it important to develop the Kingdom’s economy by increasing employment opportunities?"
        resp = qs.query(query, self.corpus_id, summarizer="vectara-summary-ext-v1.3.0", response_lang="ar")

        self.logger.info(render_markdown(query, resp, rtl=True))


    def test_arabic_with_summary_gpt3_5(self):
        """
        Tests that we can run with shorter context
        """
        qs = self.query_service

        context_config = {
            'charsBefore': 0, # Ignored if sentences specified
            'charsAfter': 0,
            'sentencesBefore': 1,  # For our test we reduce from 2 (default)
            'sentencesAfter': 1,
            'startTag': '<b>',
            'endTag': '</b>'
        }

        query = "Is it important to develop the Kingdom’s economy by increasing employment opportunities?"
        resp = qs.query(query, self.corpus_id, summarizer="vectara-summary-ext-v1.2.0",
                        context_config=context_config)

        self.logger.info(render_markdown(query, resp))

    def test_no_summary(self):
        qs = self.query_service

        query = "Is it important to develop the Kingdom’s economy by increasing employment opportunities?"
        resp = qs.query(query, self.corpus_id, summary=False)

        self.logger.info(render_markdown(query, resp, expect_summary=False))

        #self.logger.info("Request was: " + json.dumps(self.client.get_requests()[-1],indent=4))
        self.logger.info("Response was: " + json.dumps(asdict(resp, dict_factory=_custom_asdict_factory), indent=4))





