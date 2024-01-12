import unittest
from test.base import BaseClientTest
from vectara_client.enums import ApiKeyType
from vectara_client.core import Factory
import json
from requests.exceptions import HTTPError
import time

class ApiKeyTest(BaseClientTest):

    def setUp(self):
        super().setUp()
        self.upload_test_doc("./resources/research/D19-5819.pdf")

    def _create_api_key(self, description=None):
        if not description:
            description = f"Test key to test {self.id()}"

        # Create an API Key.
        api_key = self.admin_service.create_api_key(self.corpus_id, ApiKeyType.API_KEY_TYPE__SERVING,
                                                    description=description)
        self.logger.info(f"Created API key for corpus [{self.corpus_id}] with value [{api_key}]")
        return api_key

    def _create_api_key_client(self, api_key):
        # Create a client instance where we dynamically create it with the API key.
        config = {
            'customer_id': str(self.admin_service.customer_id),
            'auth': {
                'api_key': api_key
            }
        }
        api_key_client = Factory(config_json=json.dumps(config)).build()
        return api_key_client

    def _test_success_query(self, api_key_client):
        # Test successful.
        resp = api_key_client.query_service.query("Why was spark created", self.corpus_id, summary=False)
        self.assertEqual(len(resp.document), 1, "We were expecting our sigmoid "
                                                "document but there were none")
        self.assertTrue(len(resp.response) >= 1, "We were expecting response sections but received none.")

    def _test_forbidden(self, api_key_client):
        # Test denial (NB: Check time to revoke respected).
        with self.assertRaises(HTTPError) as context:
            resp = api_key_client.query_service.query("Why was spark created", self.corpus_id, summary=False)
        self.assertTrue(context.exception.response.status_code == 401)

    def test_api_key_deletion(self):
        """
        Tests API key deletion and implicitly creation
        https://docs.vectara.com/docs/api-reference/api-keys/create-api-key
        https://docs.vectara.com/docs/api-reference/api-keys/delete-api-key
        """
        api_key = self._create_api_key()
        api_key_client = self._create_api_key_client(api_key)
        self._test_success_query(api_key_client)

        # Delete the key.
        self.admin_service.delete_api_key(api_key)

        self._test_forbidden(api_key_client)


    def test_api_key_disable(self):
        """
        Tests API key disable/enable and implicitly creation
        https://docs.vectara.com/docs/api-reference/api-keys/create-api-key
        https://docs.vectara.com/docs/api-reference/api-keys/enable-api-key
        """
        api_key = self._create_api_key()
        api_key_client = self._create_api_key_client(api_key)
        self._test_success_query(api_key_client)

        # Disable the key.
        self.admin_service.update_api_key(api_key, False)

        # Create pause as operation isn't instantaneous.
        self.logger.info("Waiting 5 seconds to let API eventual consistency to eventuate.")
        time.sleep(5)

        self._test_forbidden(api_key_client)

        # Enable the key.
        self.admin_service.update_api_key(api_key, True)

        # Create pause as operation isn't instantaneous.
        self.logger.info("Waiting 5 seconds to let API eventual consistency to eventuate.")
        time.sleep(5)

        self._test_success_query(api_key_client)



    def test_list_api_keys(self):
        """
        Test List API Keys.

        """

        # Get all API keys for this corpus.
        api_keys = self.admin_service.list_api_keys(corpus_id=self.corpus_id)

        # Delete each one.
        for api_key in api_keys:
            self.admin_service.delete_api_key(api_key.apiKey.id)

        api_keys = self.admin_service.list_api_keys(corpus_id=self.corpus_id)
        self.assertEqual(0, len(api_keys), f"We were expecting no API keys but found [{len(api_keys)}]")

        # Create A list of API Keys, with different type/status
        api_key_1 = self._create_api_key("test_list_api_keys_1")

        api_keys = self.admin_service.list_api_keys(corpus_id=self.corpus_id)
        self.assertEqual(1, len(api_keys), f"We were expecting one API keys but found [{len(api_keys)}]")

        # Test Corpus Filtering by putting a non-existant corpus Id here. As filtering happens
        # client side, we won't hit any issues of "corpus not found" exception.
        api_keys = self.admin_service.list_api_keys(corpus_id=10000001)
        self.assertEqual(0, len(api_keys), f"We were expecting no API keys but found [{len(api_keys)}]")

        api_keys = self.admin_service.list_api_keys(corpus_id=self.corpus_id, enabled=False)
        self.assertEqual(0, len(api_keys), f"We were expecting no API keys but found [{len(api_keys)}]")



        # TODO Test what happens when we don't have permission to create an API key (OAuth key without + API Key)


if __name__ == '__main__':
    unittest.main()
