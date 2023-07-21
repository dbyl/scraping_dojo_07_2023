import sys
import json
import os
import time
import logging
import html5lib
import traceback
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
from typing import List, Union
from bs4 import BeautifulSoup
from enum import Enum, IntEnum
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from environment_config import CustomEnvironment


url_to_scrap=CustomEnvironment.get_input_url()
json_file=CustomEnvironment.get_output_file()
proxy=CustomEnvironment.get_proxy()
print(proxy)
print(url_to_scrap)
print(json_file)


class ScrapWebpage:


    def __init__(self, url_to_scrap: str, to_json: bool=True) -> None:
        self.url_to_scrap = url_to_scrap
        self.to_json = to_json

    def scrap_data(self) -> str:
        try:
            driver = webdriver.Chrome()
            driver.set_window_size(1400,1000)
            driver.get(self.url_to_scrap)
            element_selector = ".quote"
            waiting_timeout = 15
            element_present = EC.presence_of_element_located((By.CSS_SELECTOR, element_selector))
            WebDriverWait(driver, waiting_timeout).until(element_present)
            time.sleep(1)
            page = driver.page_source
            soup = BeautifulSoup(page, "html5lib")
            return soup
        except ConnectionError as e:
            logging.warning(f"ConnectionError occured: {e}. \nTry again later")
        except MissingSchema as e:
            logging.warning(f"MissingSchema occured: {e}. \nMake sure that protocol indicator is icluded in the website url")
        except HTTPError as e:
            logging.warning(f"HTTPError occured: {e}. \nMake sure that website url is valid")
        except ReadTimeout as e:
            logging.warning(f"ReadTimeout occured: {e}. \nTry again later")

    def save_to_json(self) -> json:

        with open(os.getenv("OUTPUT_FILE"), 'a') as f:
            soup = self.scrap_data()
            quotes = GetQuotes(soup).retrieve_quotes()
            for q in quotes:
                # Assuming each string is a valid JSON object
                json_object = json.dumps(q)
                f.write(json_object + '\n')

    def next_page(self):
        pass

class GetQuotes:

    def __init__(self, soup: str) -> None:
        self.soup = soup

    def retrieve_quotes(self) -> str:
        try:
            quotes = self.soup.find_all('div', {"class":"quote"})
            return quotes
        except Exception as e:
            logging.warning(f"Retrieving quotes failed: {e}\n Tracking: {traceback.format_exc()}")



#output = ScrapWebpage(url_to_scrap)
#print(output.scrap_data())

#soup = ScrapWebpage(url_to_scrap).save_to_json()
#output = GetQuotes(soup).retrieve_quotes()
#print(output)

