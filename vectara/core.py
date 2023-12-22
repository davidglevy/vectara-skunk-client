import logging
from vectara.config import ClientConfig, ApiKeyAuthConfig, loadConfig
from vectara.authn import OAuthUtil, ApiKeyUtil, BaseAuthUtil
from vectara.admin import AdminService
from vectara.index import IndexerService
from vectara.query import QueryService

import json


class Client:

    def __init__(self, customer_id: str, admin_service: AdminService,
                 indexer_service: IndexerService, query_service: QueryService):
        self.logging = logging.getLogger(self.__class__.__name__)
        logging.info("initializing Client")
        self.customer_id = customer_id
        self.admin_service = admin_service
        self.indexer_service = indexer_service
        self.query_service = query_service


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
            raise TypeError("You need to initialize the factory with one of [config_path] or [config_dict] selected")
        if self.config_path:
            self.logger.info("Loading config JSON from file [{config_path}]")
            with open(self.config_path, 'r') as f:
                self.config_json = f.read()
        elif self.config_json:
            self.logger.info("Loading config JSON from injected string to factory")
        else:
            raise TypeError("You must set either variable [config_path] or [config_dict]")

        # 2. Parse and validate the client configuration
        try:
            self.logger.info("Passing the JSON to our config")
            client_config = loadConfig(self.config_json)
        except Exception as e:
            # Raise a new exception without extra stack trace. We know the JSON failed to parse.
            raise TypeError(f"Invalid content of config: {e}") from None

        errors = client_config.validate()
        if errors:
            raise TypeError(f"Client configuration is not valid {errors}")

        # 3. Load the validated configuration into our client.

        # TODO Lets see if we can merge dataclasses with the Client classes themselves.

        auth_config = client_config.auth
        auth_type = auth_config.getAuthType()
        logging.info(f"We are processing authentication type [{auth_type}]")

        if auth_type == "ApiKey":
            authUtil = ApiKeyUtil(client_config.customer_id, client_config.auth.api_key)
        elif auth_type == "OAuth2":
            authUtil = OAuthUtil(auth_config.auth_url, auth_config.app_id, auth_config.app_client_secret, client_config.customer_id)
        else:
            raise TypeError(f"Unknown authentication type: {auth_type}")

        # TODO Use the type of authentication to validate whether we can enabled the admin service.
        admin_service = AdminService(authUtil, int(client_config.customer_id))
        indexer_service = IndexerService(authUtil, int(client_config.customer_id))
        query_service = QueryService(authUtil, int(client_config.customer_id))

        return Client(client_config.customer_id, admin_service, indexer_service, query_service)



