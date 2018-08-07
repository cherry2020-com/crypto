#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
driver = webdriver.Chrome('/Users/mingleiweng/Library/Mobile Documents/com~apple~CloudDocs/bin/chromedriver')
driver.get("http://www.python.org")
assert "Python" in driver.title
elem = driver.find_element_by_name("q")
elem.clear()
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
driver.close()
