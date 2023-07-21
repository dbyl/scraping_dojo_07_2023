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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains

from requests.exceptions import ConnectionError, HTTPError, MissingSchema, ReadTimeout

from environment_config import CustomEnvironment


url_to_scrap=CustomEnvironment.get_input_url()
json_file=CustomEnvironment.get_output_file()


class ScrapWebpage:


    def __init__(self, url_to_scrap: str, to_json: bool=False, with_proxy: bool=False) -> None:
        self.url_to_scrap = url_to_scrap
        self.to_json = to_json
        self.with_proxy = with_proxy

    def scrap_data(self) -> str:
        try:
            driver = self.proxy_activating()
            driver.set_window_size(1400,1000)
            driver.get(self.url_to_scrap)
            #self.wait_for_quotes(driver)
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

    def proxy_activating(self) -> None:
        try:
            if self.with_proxy == True:
                PROXY = CustomEnvironment.get_proxy()
                service = Service()
                options = webdriver.ChromeOptions()
                options.add_argument('--proxy-server=%s' % PROXY)
                driver = webdriver.Chrome(service=service, options=options)
                return driver
            else:
                driver = webdriver.Chrome()
                return driver
        except Exception as e:
            logging.warning(f"Setting proxy up failed: {e}\n Tracking: {traceback.format_exc()}")

    def wait_for_quotes(self, driver) -> None:
        try:
            element_selector = ".quote"
            waiting_timeout = 15
            element_present = EC.presence_of_element_located((By.CSS_SELECTOR, element_selector))
            WebDriverWait(driver, waiting_timeout).until(element_present)
        except Exception as e:
            logging.warning(f"Wait for quotes failed: {e}\n Tracking: {traceback.format_exc()}")


    def save_to_json(self) -> json:

        with open(os.getenv("OUTPUT_FILE"), 'a') as f:
            soup = self.scrap_data()
            quotes = GetQuotes(soup).retrieve_quotes()
            for q in quotes:
                # Assuming each string is a valid JSON object
                json_object = json.dumps(q)
                f.write(json_object + '\n')

    def next_page_if_exists(self) -> None:
        driver = self.proxy_activating()

        try:
            wait = WebDriverWait(driver, 2)
            accept = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'next')))
            accept.click()
        except Exception as e: 
            logging.warning(f"Failed: {e}\n Tracking: {traceback.format_exc()}")
        
        """
        try:
            next_page_button = soup.find('li', {'class': 'next'})
            if next_page_button:
                flag = True
                #driver.find_element(By.CSS_SELECTOR, '.next').click()
                #next_page_button_element = driver.find_element(By.CLASS_NAME, 'next')
                wait = WebDriverWait(driver, 2)
                accept = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'next')))
                actions = ActionChains(driver)
                actions.move_to_element(accept).click().perform()
                #print(next_page_button_element)
                #next_page_button.click()
                return flag
            else:
                logging.info("No more pages.")
                flag = False
                return flag
        except Exception as e:
            logging.warning(f"Looking for next page failed: {e}\n Tracking: {traceback.format_exc()}")
    """

    def go_through_all_pages(self) -> List[str]:
        list_of_quotes = list()
        flag = True

        while flag==True:
            soup = self.scrap_data()
            list_of_quotes.append(GetQuotes(soup).retrieve_quotes())
            flag = self.next_page_if_exists()

        return list_of_quotes

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

output = ScrapWebpage(url_to_scrap).go_through_all_pages()
#output = GetQuotes(soup).go_through_all_pages()
output

