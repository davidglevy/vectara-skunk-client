import json
import logging

import os
import argparse
import time
import feedparser
import re
import subprocess
import sys

from bloom_filter import BloomFilter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from pyhtml2pdf import converter
from usp.tree import sitemap_tree_for_homepage


from urllib.parse import urlparse
# from urlparse import urlparse  # Python 2
from pathlib import Path

from cralwer_util import CrawlerUtil, IndexerUtil, JwtAuthenticator


token = None
appclient_id = None
appclient_secret = None
seen_pages = BloomFilter(max_elements=50000, error_rate=0.01)

crawler_util = CrawlerUtil()

def extract_links(url: str, timeout: int = 2, install_driver: bool = True):
    webdriver_options = Options()
    webdriver_prefs = {}
    driver = None

    webdriver_options.add_argument('--headless')
    webdriver_options.add_argument('--disable-gpu')
    webdriver_options.add_argument('--no-sandbox')
    webdriver_options.add_argument('--disable-dev-shm-usage')
    webdriver_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    webdriver_options.experimental_options['prefs'] = webdriver_prefs

    if install_driver:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=webdriver_options)
    else:
        driver = webdriver.Chrome(options=webdriver_options)
    driver.get(url)
    try:
        WebDriverWait(driver, timeout).until(staleness_of(driver.find_element(by=By.TAG_NAME, value='html')))
    except TimeoutException:
        elems = driver.find_elements(By.XPATH, '//a[@href]')
        return map(lambda elem: elem.get_attribute("href"), elems)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(e, exc_type, exc_tb.tb_lineno)
        raise
    return

def crawl_url(url: str, crawl_id: str, customer_id: int, corpus_id: int,
              crawl_pattern: re, idx_address: str, retry: bool = False,
              prefetched_filename: str = None, pdf_driver: str = 'chrome',
              install_chrome_driver: bool = True):
    global token, appclient_id, appclient_secret

    if crawl_pattern != None and not crawl_pattern.match(url):
        return "Crawl pattern not matched", False

    Path("pdfs").mkdir(parents=True, exist_ok=True)

    logging.info(f"Crawling [{str}]")
    if prefetched_filename:
        logging.info(f"Pre-fetched File name is not blank: [{prefetched_filename}]")

    filename = "pdfs/" + crawler_util.convertUrlToFile(url)
    logging.info(f"We will save data to file [{filename}]")
    if retry == False or prefetched_filename != None:
        logging.info("Grabbing %s", url)
        # r = requests.get(url)
        if pdf_driver == 'chrome':
          res = converter.convert(url, filename,
                                  install_driver=install_chrome_driver)
        elif pdf_driver == 'wkhtmltopdf':
          list_files = subprocess.run(["wkhtmltopdf", url, filename])
    else:
        filename = prefetched_filename



    print("Converting page to PDF")
    with open(filename, 'rb') as file_ref:
        if pdf_driver == 'chrome':
            files = {
                "file": (f"{crawl_id}-{url}", file_ref, 'application/pdf'),
            }
        elif pdf_driver == 'wkhtmltopdf':
            url_obj = urlparse(url)
            url_no_fragment=url_obj._replace(fragment="").geturl()

            files = {
                "file": (f"{crawl_id}-{url_no_fragment}", file_ref, 'application/pdf'),
            }
        meta = {
            "doc_metadata": json.dumps({
                "url": url,
                "crawl_id": crawl_id
            })
        }

        index_url = f"https://{idx_address}/upload?c={customer_id}&o={corpus_id}"
        response, success = upload_to_index(index_url, files, meta)
    os.remove(filename)

    return response, success

def crawl_rss(feed_url: str, crawl_id: str, customer_id: int, corpus_id: int,
              crawl_pattern: re, idx_address: str, pdf_driver: str = 'chrome',
              install_chrome_driver: bool = True):
    feed = feedparser.parse(feed_url)
    for entry in feed['entries']:
        try:
            crawl_url(entry.link, crawl_id, customer_id, corpus_id,
                      crawl_pattern, idx_address, pdf_driver=pdf_driver,
                      install_chrome_driver=install_chrome_driver)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logging.error("Error crawling %s", entry.link)
    return

def crawl_recursive(url: str, max_depth: int, crawl_id: str, customer_id: int,
                    corpus_id: int, crawl_pattern: re, idx_address: str,
                    current_depth: int = 1, pdf_driver: str = 'chrome',
                    install_chrome_driver: bool = False):
    global seen_pages
    try:
        crawl_url(url, crawl_id, customer_id, corpus_id, crawl_pattern,
                  idx_address, pdf_driver=pdf_driver,
                  install_chrome_driver=install_chrome_driver)

        if current_depth < max_depth:
            links = extract_links(url, install_driver=install_chrome_driver)
            for link in links:
                if (link != None and seen_pages != None and link not in seen_pages):
                    seen_pages.add(link)
                    if crawl_pattern == None or crawl_pattern.match(link):
                        crawl_recursive(link, max_depth, crawl_id, customer_id,
                                        corpus_id, crawl_pattern, idx_address,
                                        current_depth+1,
                                        pdf_driver=pdf_driver,
                                        install_chrome_driver=install_chrome_driver)
        else:
            logging.info("Maximum depth of recursive crawl reached")
    except KeyboardInterrupt:
        raise
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(e, exc_type, exc_tb.tb_lineno)
        logging.error("Error crawling %s", url)

def crawl_sitemap(url: str, crawl_id: str, customer_id: int,
                  corpus_id: int, crawl_pattern: re, idx_address: str,
                  pdf_driver: str = 'chrome', install_chrome_driver: bool = True):
    tree = sitemap_tree_for_homepage(url)
    for page in tree.all_pages():
        try:
            crawl_url(page.url, crawl_id, customer_id, corpus_id, crawl_pattern,
                      idx_address, pdf_driver=pdf_driver,
                      install_chrome_driver=install_chrome_driver)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logging.error("Error crawling %s", page.url)
    return

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

    parser = argparse.ArgumentParser(description="Vectara web crawler example")

    parser.add_argument("--url", help="The base URL to start crawling from.", required=True)
    parser.add_argument("--crawl-type",
                        help="Can be one of: single-page, sitemap, rss, or recursive.",
                        choices=['sitemap', 'rss', 'recursive', 'single-page'],
                        default="sitemap")

    parser.add_argument("--depth", type=int, help="Maximum depth of pages to crawl", default=3)
    parser.add_argument("--delete-pdfs", help="Whether we should delete scraped PDFs", default=False)

    parser.add_argument("--crawl-pattern", help="Pattern to keep the crawl to")

    parser.add_argument("--crawl-id", help="ID for the crawl for filtering", default="")

    parser.add_argument("--customer-id", type=int, help="Unique customer ID in Vectara platform.", required=True)
    parser.add_argument("--corpus-id", 
                        type=int, 
                        required=True,
                        help="Corpus ID to which data will be indexed and queried from.")

    parser.add_argument("--indexing-endpoint", help="The endpoint of indexing server.",
                        default="api.vectara.io")

    parser.add_argument("--appclient-id", required=True, help="This appclient should have enough rights.")
    parser.add_argument("--appclient-secret", required=True)
    parser.add_argument("--auth-url", help="The auth url for this customer.",
                        default="")

    parser.add_argument("--install-chrome-driver",
                        action=argparse.BooleanOptionalAction,
                        help="Whether the crawler should try to install the Chrome Driver for exracting links",
                        default=True)
    parser.add_argument("--pdf-driver",
                        choices=['chrome', 'wkhtmltopdf'],
                        help="What software to use to convert webpages to PDFs",
                        default='chrome')

    args = parser.parse_args()

    if args:

        customer_id = args.customer_id
        logging.info(f"Found customer Id [{customer_id}]")

        auth_url = args.auth_url
        app_client_id = args.appclient_id
        app_client_secret = args.appclient_secret

        authenticator = JwtAuthenticator(auth_url, app_client_id, app_client_secret, customer_id)
        authenticator.authenticate()

        #token = initialize_jwt_token(auth_url, app_client_id, app_client_secret)

        delete_pdfs = args.delete_pdfs

        crawl_pattern = None
        if args.crawl_pattern != None:
            crawl_pattern = re.compile(args.crawl_pattern)
        
            if args.crawl_type == 'single-page':
                error, status = crawl_url(url=args.url,
                                  crawl_id=args.crawl_id,
                                  customer_id=args.customer_id,
                                  corpus_id=args.corpus_id,
                                  crawl_pattern=crawl_pattern,
                                  idx_address=args.indexing_endpoint,
                                  retry=False,
                                  prefetched_filename=None,
                                  pdf_driver=args.pdf_driver,
                                  install_chrome_driver=args.install_chrome_driver)
            elif args.crawl_type == 'sitemap':
                crawl_sitemap(url=args.url,
                              crawl_id=args.crawl_id,
                              customer_id=args.customer_id,
                              corpus_id=args.corpus_id,
                              crawl_pattern=crawl_pattern,
                              idx_address=args.indexing_endpoint,
                              pdf_driver=args.pdf_driver,
                              install_chrome_driver=args.install_chrome_driver)
            elif args.crawl_type == 'rss':
                crawl_rss(url=args.url,
                          crawl_id=args.crawl_id,
                          customer_id=args.customer_id,
                          corpus_id=args.corpus_id,
                          crawl_pattern=crawl_pattern,
                          idx_address=args.indexing_endpoint,
                          pdf_driver=args.pdf_driver,
                          install_chrome_driver=args.install_chrome_driver)
            elif args.crawl_type == 'recursive':
                crawl_recursive(url=args.url,
                                max_depth=args.depth,
                                crawl_id=args.crawl_id,
                                customer_id=args.customer_id,
                                corpus_id=args.corpus_id,
                                crawl_pattern=crawl_pattern,
                                idx_address=args.indexing_endpoint,
                                pdf_driver=args.pdf_driver,
                                install_chrome_driver=args.install_chrome_driver)

        else:
            logging.error("Could not generate an auth token. Please check your credentials.")
