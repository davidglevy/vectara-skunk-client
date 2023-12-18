import unittest
import logging
from vectara.config import ClientConfig, ApiKeyAuthConfig, loadConfig

logging.basicConfig(
        format=logging.BASIC_FORMAT, level=logging.INFO)


class ClientConfigTest(unittest.TestCase):
    def testLoadConfigApiKeyConfig(self):

        customer_id = "12344"
        api_key = "BLAH_KEY"

        config_dict = f"""{{
            "customer_id" : "{customer_id}",
            "auth" : {{
                "api_key" : "{api_key}"
            }}
        }}"""

        result = loadConfig(config_dict)

        self.assertEqual(result.customer_id, customer_id)
        self.assertIsInstance(result.auth, ApiKeyAuthConfig)
        self.assertEqual(result.auth.api_key, api_key)

    def testLoadConfigOAuth2Valid(self):

        customer_id = "12344"
        app_id = "MY_APP_ID"
        app_api_secret = "BLAH_KEY"

        config_dict = f"""{{
            "customer_id" : "{customer_id}",
            "auth" : {{
                "app_id" : "{app_id}",
                "app_api_secret" : "{app_api_secret}"
            }}
        }}"""

        result = loadConfig(config_dict)

    def testLoadConfigOAuth2MissingAppId(self):

        customer_id = "12344"
        app_id = "MY_APP_ID"
        app_api_secret = "BLAH_KEY"

        config_dict = f"""{{
            "customer_id" : "{customer_id}",
            "auth" : {{
                "app_api_secret" : "{app_api_secret}"
            }}
        }}"""

        with self.assertRaises(TypeError) as cm:
            result = loadConfig(config_dict)

        message = str(cm.exception)
        self.assertIn('Could not use polymorphism to cast auth to either OAuth2 or API Key config', message)


