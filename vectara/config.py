import logging
from dataclasses import dataclass
from dacite import from_dict, Config, UnexpectedDataError
from typing import Optional, Union
import json

"""
Collection of dataclasses related to the configuration of the application.

"""
logger = logging.getLogger(__name__)

@dataclass
class BaseAuthConfig:

    def getAuthType(self) -> str:
        raise NotImplementedError("You must implement this method to return the String type of the auth")

@dataclass
class ApiKeyAuthConfig(BaseAuthConfig):
    api_key: str

    def getAuthType(self) -> str:
        return "ApiKey"

@dataclass
class OAuth2AuthConfig(BaseAuthConfig):
    auth_url: Optional[str]
    app_id: str
    app_client_secret: str

    def getAuthType(self) -> str:
        return "OAuth2"

    def validate(self):
        pass


@dataclass
class ClientConfig:
    """
    Wrapper for all configuration needed to work with Vectara.
    """

    customer_id: str
    auth: Union[ApiKeyAuthConfig, OAuth2AuthConfig]

    def validate(self) -> [str]:
        errors = []

        if not self.customer_id:
            errors.append(f"In [{__class__.__name__}] You must define the field [customer_id]")



        return errors

def _tryCreateAuth(data_class, input):
    try:
        from_dict(data_class=data_class, data=input, config=Config(strict=True))
        return True, None
    except Exception as e:
        return False, str(e)

def loadConfig(config: str) -> ClientConfig:
    """
    Loads our configuration from JSON onto our data classes.

    :param config: the input configuration in JSON format.
    :return: the parsed client configuration1
    :raises TypeError: if the configuration cannot be parsed correctly
    """
    logger.info(f"Loading config from {config}")

    config_dict = json.loads(config)

    # First we're going to manually try each Authentication Type for better logging.
    # This is because the dicate library just gives the user a generic error
    # without any logging.
    auth = config_dict["auth"]
    if (auth):
        oauth2_success, oauth2_error_msg = _tryCreateAuth(OAuth2AuthConfig, auth)
        api_key_success, api_key_error_msg = _tryCreateAuth(ApiKeyAuthConfig, auth)

        if not oauth2_success and not api_key_success:
            logger.error(f"Invalid Authentication Configuration:\n{json.dumps(auth, indent=4)}")
            logger.error(f"Unable to cast auth to OAuth2 configuration block: {oauth2_error_msg}")
            logger.error(f"Unable to cast auth to API Key configuration block: {api_key_error_msg}")

            raise TypeError(f"Could not use polymorphism to cast auth to either OAuth2 or API Key config, see errors above in log.")



    logger.info("Parsing config")
    try:
        return from_dict(data_class=ClientConfig, data=config_dict, config=Config(strict=True))
    except UnexpectedDataError as e:
        raise TypeError(f"Unable to build configuration: {e}") from None

