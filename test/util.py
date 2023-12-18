import yaml
import json

def loadTestConfig(config_name: str):
    with open(".vectara_test_config", "r") as yaml_stream:
        print("Loading test credentials")
        creds = yaml.safe_load(yaml_stream)
        return creds[config_name]

def loadTestConfigAsJson(config_name: str):
    config = loadTestConfig(config_name)


    final_config = {
        "customer_id" : config["customer_id"],
        "auth" : {
            "app_id" : config["app_client_id"],
            "app_client_secret" : config["app_client_secret"]
        }
    }

    if "auth_url" in config:
        final_config["auth"]["auth_url"] = config["auth_url"]

    return json.dumps(final_config)

