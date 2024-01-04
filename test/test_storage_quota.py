import unittest
from test.base import BaseClientTest
from test.util import check_metadata


class StorageQuotaTest(BaseClientTest):
    """
    Tests that each index or upload requests returns the same corpus size calculation if summed incrementally.
    """

    def setUp(self):
        super().setUp()

    def test_upload_size(self):
        """
        Tests that the corpus size is equal to each upload.
        :return:
        """

        resp1 = self.upload_test_doc("./resources/research/D19-5819.pdf", force=True)
        resp2 = self.upload_test_doc("./resources/fair_work_australia/C2023A00043.pdf", force=True)
        resp3 = self.upload_test_doc("./resources/fair_work_australia/F2024C00002.pdf", force=True)

        total_consumed = 0
        for resp in [resp1, resp2, resp3]:
            total_consumed += int(resp.response.quotaConsumed.numChars) + int(resp.response.quotaConsumed.numMetadataChars)

        self.check_total_consumed(total_consumed)

    def check_total_consumed(self, total_consumed):
        self.logger.info(f"Total consumed is [{total_consumed}]")
        self.logger.info("Calculating corpus size")
        resp = self.admin_service.calculate_corpus_size(self.corpus_id)
        corpus_size = int(resp.size.size)
        self.logger.info(f"Corpus size is [{corpus_size}]")
        # Check corpus size from admin service.
        self.assertEqual(corpus_size, total_consumed, f"The expected corpus size [{corpus_size}] is different "
                                                      f"from the total sum from each response [{total_consumed}]")

    def test_index_size(self):
        """
        Tests that the corpus size is equal to each index response quota consumed.
        :return:
        """
        resp1 = self.index_test_doc("./resources/filter_attributes/document_1.json", force=True)
        resp2 = self.index_test_doc("./resources/filter_attributes/document_2.json", force=True)
        resp3 = self.index_test_doc("./resources/filter_attributes/document_3.json", force=True)

        total_consumed = 0
        for resp in [resp1, resp2, resp3]:
            total_consumed += int(resp.quotaConsumed.numChars) + int(resp.quotaConsumed.numMetadataChars)

        self.check_total_consumed(total_consumed)


if __name__ == '__main__':
    unittest.main()