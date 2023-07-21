import json
import logging
import os
import time
import traceback
from typing import List, Tuple

import html5lib
import jsbeautifier
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, HTTPError, MissingSchema, ReadTimeout
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from environment_config import CustomEnvironment

url = CustomEnvironment.get_input_url()
json_file = CustomEnvironment.get_output_file()


class ScrapWebpage:
    def __init__(
        self,
        url: str,
        with_proxy: bool = False,
        start_page: int = 1,
    ) -> None:
        self.url = url
        self.with_proxy = with_proxy
        self.start_page = start_page

    def scrap_data(self) -> Tuple[BeautifulSoup, bool]:
        try:
            driver = self.proxy_activating()
            driver.set_window_size(1400, 1000)
            url_to_scrap = self.preparing_url()
            driver.get(url_to_scrap)
            flag = self.wait_for_quotes(driver)
            time.sleep(1)
            page = driver.page_source
            soup = BeautifulSoup(page, "html5lib")
            return soup, flag
        except ConnectionError as e:
            logging.warning(f"ConnectionError occured: {e}. \nTry again later")
        except MissingSchema as e:
            logging.warning(
                f"MissingSchema occured: {e}. \nMake sure that protocol indicator is icluded in the website url"
            )
        except HTTPError as e:
            logging.warning(
                f"HTTPError occured: {e}. \nMake sure that website url is valid"
            )
        except ReadTimeout as e:
            logging.warning(f"ReadTimeout occured: {e}. \nTry again later")

    def preparing_url(self):
        try:
            url_to_scrap = "".join([url, "page/", str(self.start_page)])
            return url_to_scrap
        except Exception as e:
            logging.warning(
                f"Preparing url failed: {e}\n Tracking: {traceback.format_exc()}"
            )

    def proxy_activating(self) -> None:
        try:
            if self.with_proxy == True:
                PROXY = CustomEnvironment.get_proxy()
                service = Service()
                options = webdriver.ChromeOptions()
                options.add_argument("--proxy-server=%s" % PROXY)
                driver = webdriver.Chrome(service=service, options=options)
                return driver
            else:
                driver = webdriver.Chrome()
                return driver
        except Exception as e:
            logging.warning(
                f"Setting proxy up failed: {e}\n Tracking: {traceback.format_exc()}"
            )

    def wait_for_quotes(self, driver) -> bool():
        try:
            element_selector = ".quote"
            waiting_timeout = 15
            element_present = EC.presence_of_element_located(
                (By.CSS_SELECTOR, element_selector)
            )
            WebDriverWait(driver, waiting_timeout).until(element_present)
            flag = True
            return flag
        except Exception:
            flag = False
            logging.info(f"No more pages.")
            return flag

    def go_through_all_pages(self) -> List[str]:
        try:
            flag = True
            retrived_quotes = list()
            while flag:
                soup, flag = self.scrap_data()
                quotes = GetQuotes(soup).get_data()
                retrived_quotes.append(quotes)
                if soup.find("li", attrs={"class": "next"}) is None:
                    flag = False
                self.start_page += 1

            return retrived_quotes
        except Exception as e:
            logging.warning(f"FAIL: {e}\n Tracking: {traceback.format_exc()}")

    def save_to_json(self) -> None:
        all_quotes_list = list()
        with open(os.getenv("OUTPUT_FILE"), "a") as f:
            list_of_quotes = self.go_through_all_pages()
            for quotes in list_of_quotes:
                for quote in quotes:
                    quote_obj = {
                        "text": GetQuoteDetails(quote).get_text(),
                        "by": GetQuoteDetails(quote).get_author(),
                        "tags": GetQuoteDetails(quote).get_tags(),
                    }
                    options = jsbeautifier.default_options()
                    options.indent_size = 4
                    all_quotes_list.append(quote_obj)
            json_object_better = jsbeautifier.beautify(
                json.dumps(all_quotes_list, separators=(", ", ": ")), options
            )
            f.write(json_object_better + "\n")


class GetQuotes:
    def __init__(self, soup: str) -> None:
        self.soup = soup

    def get_data(self) -> str:
        try:
            quotes = self.soup.find_all("div", {"class": "quote"})
            return quotes
        except Exception as e:
            logging.warning(
                f"Retrieving quotes failed: {e}\n Tracking: {traceback.format_exc()}"
            )


class GetQuoteDetails:
    def __init__(self, quote: str) -> None:
        self.quote = quote

    def get_author(self) -> str:
        try:
            author = self.quote.find("small", class_="author").text
            return author
        except Exception as e:
            logging.warning(
                f"Retrieving author failed: {e}\n Tracking: {traceback.format_exc()}"
            )

    def get_text(self) -> str:
        try:
            text = self.quote.find("span", class_="text").text.strip("“”'")
            return text
        except Exception as e:
            logging.warning(
                f"Retrieving text failed: {e}\n Tracking: {traceback.format_exc()}"
            )

    def get_tags(self) -> List[str]:
        try:
            tags = self.quote.find("div", class_="tags").find_all("a")
            tags_list = list()
            for tag in tags:
                tags_list.append(tag.text)
            return tags_list
        except Exception as e:
            logging.warning(
                f"Retrieving tags failed: {e}\n Tracking: {traceback.format_exc()}"
            )


if __name__ == "__main__":
    output = ScrapWebpage(url)
    output.save_to_json()
