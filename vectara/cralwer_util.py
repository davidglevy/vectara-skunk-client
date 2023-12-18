
#def initialize_jwt_token(auth_url: str, appclient_id: str, appclient_secret: str):
#    """Connect to the server and get a JWT token."""
#    token_endpoint = f"{auth_url}/oauth2/token"
#    session = OAuth2Session(
#        appclient_id, appclient_secret, scope="")
#    token = session.fetch_token(token_endpoint, grant_type="client_credentials")
#    return token["access_token"]

class IndexerUtil:

    def __init__(self, customer_id : str, corpus_id : str, jwt_token : str):
        self.customer_id = customer_id
        self.corpus_id = corpus_id
        self.jwt_token = jwt_token

    def update_jwt_token(self, jwt_token):
        self.jwt_token = jwt_token

    def upload_to_index(self, files: dict, meta):
        print("Uploading {} to Vectara")

        post_headers = {
            "Authorization": f"Bearer {self.jwt_token}"
        }

        response = requests.post(

            files=files,
            data=meta,
            verify=True,
            headers=post_headers)

        # if response.status_code == 401 and retry == False:
        # This used to have code to retry, TODO Refactor into flow.
        # token = _get_jwt_token(auth_url, appclient_id, appclient_secret)
        # crawl_url(url, crawl_id, customer_id, corpus_id, crawl_pattern,
        #          idx_address, True, filename, pdf_driver,
        #          install_chrome_driver=install_chrome_driver)

        if response.status_code != 200:
            # FIXME This should raise an exception.
            logging.error("REST upload failed with code %d, reason %s, text %s",
                          response.status_code,
                          response.reason,
                          response.text)
            return response, False

        return response, True

class CrawlerUtil:

    def __init__(self):
        self.file_index = 0

    def convertUrlToFile(self, url):
        parsed_uri = urlparse(url)


        host = parsed_uri.hostname
        host = re.sub("\.", "-", host)

        path = parsed_uri.path
        path = re.sub("/", "-", path)

        query = parsed_uri.query
        print(f"Here are the params {query}")
        query_result = []
        if query and len(query) > 0:
            query_parts = query.split("&")
            for query_part in query_parts:
                key_value = re.sub("=", "-", query_part)
                query_result.append(key_value)
        query = "_".join(query_result)


        if path.startswith("-"):
            path = path[1:]

        result = host

        if len(path) > 0:
            result = result + "_" + path

        if len(query) > 0:
            result = result + "_" + query

        self.file_index += 1

        result += f".{self.file_index}"


        result += ".pdf"

        return result








