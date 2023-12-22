import yaml
import json
import logging

logger = logging.getLogger(__name__)

def loadTestConfig(config_name: str):
    with open(".vectara_test_config", "r") as yaml_stream:
        logger.info("Loading test credentials")
        creds = yaml.safe_load(yaml_stream)
        return creds[config_name]

def loadTestConfigAsJson(config_name: str):
    config = loadTestConfig(config_name)


    if 'app_client_id' in config:
        logger.info("Loading OAuth style config")
        final_config = {
            "customer_id" : config["customer_id"],
            "auth" : {
                "app_id" : config["app_client_id"],
                "app_client_secret" : config["app_client_secret"]
            }
        }

        if "auth_url" in config:
            final_config["auth"]["auth_url"] = config["auth_url"]
    elif 'api_key' in config:
        logger.info("Loading API key style config")
        final_config = {
            "customer_id" : config["customer_id"],
            "auth" : {
                "api_key" : config['api_key']
            }
        }

    else:
        raise TypeError("Expecting either an [app_client_id] or [api_key] "
                        "for OAuth2/ApiKey authentication in test config")

    return json.dumps(final_config)



