import unittest
from test.base import BaseClientTest
from vectara.util import render_markdown


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
        qs = self.query_service

        query = "Is it important to develop the Kingdom’s economy by increasing employment opportunities?"
        resp = qs.query(query, self.corpus_id, summarizer="vectara-summary-ext-v1.2.0")

        self.logger.info(render_markdown(query, resp))

    def test_no_summary(self):
        qs = self.query_service

        query = "Is it important to develop the Kingdom’s economy by increasing employment opportunities?"
        resp = qs.query(query, self.corpus_id, summary=False)

        self.logger.info(render_markdown(query, resp, expect_summary=False))





