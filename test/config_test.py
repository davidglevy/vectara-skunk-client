import unittest
import logging
from vectara.client.config import ApiKeyAuthConfig, loadConfig

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

    def testLoadConfigInvalidUnknownFieldAuth(self):

        customer_id = "12344"
        api_key = "BLAH_KEY"

        config_dict = f"""{{
            "customer_id" : "{customer_id}",
            "auth" : {{
                "api_key" : "{api_key}",
                "extra_field" : "Ha"
            }}
        }}"""

        with self.assertRaises(TypeError) as cm:
            loadConfig(config_dict)

        message = str(cm.exception)
        self.assertIn('Could not use polymorphism to cast auth to either OAuth2 or API Key config', message)

    def testLoadConfigInvalidUnknownFieldTop(self):

        customer_id = "12344"
        api_key = "BLAH_KEY"

        config_dict = f"""{{
            "customer_id" : "{customer_id}",
            "extra_field" : "Ha",
            "auth" : {{
                "api_key" : "{api_key}"
            }}
        }}"""

        with self.assertRaises(TypeError) as cm:
            loadConfig(config_dict)

        message = str(cm.exception)
        self.assertIn('can not match "extra_field" to any data class field', message)


    def testLoadConfigOAuth2Valid(self):

        customer_id = "12344"
        app_id = "MY_APP_ID"
        app_api_secret = "BLAH_KEY"

        config_dict = f"""{{
            "customer_id" : "{customer_id}",
            "auth" : {{
                "app_id" : "{app_id}",
                "app_client_secret" : "{app_api_secret}"
            }}
        }}"""

        result = loadConfig(config_dict)

    def testLoadConfigOAuth2ValidUrl(self):

        customer_id = "12344"
        app_id = "MY_APP_ID"
        app_api_secret = "BLAH_KEY"

        config_dict = f"""{{
            "customer_id" : "{customer_id}",
            "auth" : {{
                "app_id" : "{app_id}",
                "app_client_secret" : "{app_api_secret}",
                "auth_url" : "https://some.url/"
                
            }}
        }}"""

        result = loadConfig(config_dict)

        print(result)

    def testLoadConfigOAuth2Strict(self):
        customer_id = "12344"
        app_id = "MY_APP_ID"
        app_api_secret = "BLAH_KEY"

        config_dict = f"""{{
            "customer_id" : "{customer_id}",
            "auth" : {{
                "app_id" : "{app_id}",
                "app_client_secret" : "{app_api_secret}",
                "auth_url" : "https://some.url/",
                "what_the" : "should_throw_error"

            }}
        }}"""

        with self.assertRaises(TypeError) as cm:
            result = loadConfig(config_dict)

        message = str(cm.exception)
        self.assertIn('Could not use polymorphism to cast auth to either OAuth2 or API Key config', message)

    def testLoadConfigOAuth2MissingAppId(self):

        customer_id = "12344"
        app_id = "MY_APP_ID"
        app_api_secret = "BLAH_KEY"

        config_dict = f"""{{
            "customer_id" : "{customer_id}",
            "auth" : {{
                "app_client_secret" : "{app_api_secret}"
            }}
        }}"""

        with self.assertRaises(TypeError) as cm:
            result = loadConfig(config_dict)

        message = str(cm.exception)
        self.assertIn('Could not use polymorphism to cast auth to either OAuth2 or API Key config', message)


