import logging
from vectara.config import ClientConfig, ApiKeyAuthConfig, loadConfig
from authn import OAuthUtil, ApiKeyUtil

import json


class Client:

    def __init__(self):
        self.logging = logging.getLogger(self.__class__.__name__)
        logging.info("initializing Client")

        #self.authentication


class Factory():

    def __init__(self, config_path=None, config_json=None):
        """
        Initialize our factory using configuration which may either be in a file or serialized in a JSON string

        :param config_path: the file containing our configuration
        :param config_json: the JSON containing our configuration
        """

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("initializing builder")
        self.config_path = config_path
        self.config_json = config_json

    def build(self):
        """
        Builds our client using the configuration which .
        :return:
        """

        # 1. Load the config whether we're doing file or we've had it passed in as a String.
        if self.config_path and self.config_json:
            raise TypeError("You need to start the factory with one of [config_path] or [config_dict] selected")
        if self.config_path:
            self.logger.info("Loading config JSON from file [{config_path}]")
            with open(self.config_path, 'r') as f:
                self.config_json = f.read()
        elif self.config_json:
            self.logger.info("Loading config JSON from injected string to factory")
        else:
            raise TypeError("You must set either variable [config_path] or [config_dict]")

        try:
            self.logger.info("Passing the JSON to our config")
            client_config = loadConfig(self.config_json)
        except Exception as e:
            # Raise a new exception without extra stack trace. We know the JSON failed to parse.
            raise TypeError(f"Invalid content of config: {e}") from None

        errors = client_config.validate()
        if errors:
            raise TypeError(f"Client configuration is not valid {errors}")

        # 2. Parse the loaded config into the real bean factories.

        # TODO Lets see if we can merge dataclasses with the Client classes themselves.

        authType = client_config.auth.getAuthType()
        logging.info(f"We are processing authentication type [{authType}]")

        if authType == "ApiKey":
            authUtil = ApiKeyUtil(client_config.customer_id, client_config.auth.api_key)
        else if authType == "OAuth2"





        return Client()



