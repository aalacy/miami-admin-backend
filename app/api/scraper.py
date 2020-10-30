#!/bin/usr/env python3

'''
	Scrape the pages from the following
	- Crunchbase
	- Instagram
	- Twitter
	- 

	@param: -q: query to search on angel.co

	e.g.
		python3 angel.py  -q "los angeles"
		
'''
import random
import time
import re
from datetime import datetime
import sys
import os
import selenium
import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome, ChromeOptions
from openpyxl import load_workbook
import pdb

from app.email import send_simple_email 

SYSCO_USERNAME = 'cmdallm@gmail.com'
SYSCO_PASSWORD = 'UpworkTest1'
SYSCO_DATASHEET = 'cost data sheet.xlsx'
SYSCO_DATASHEET_OUT = 'cost data sheet output.xlsx'

class Driver():
	basedir = os.path.abspath(os.path.dirname(__file__))
	sysco_path = f'{basedir}/data/{SYSCO_DATASHEET}'

	def __init__(self):
		self.open_chrome_browser()
		self.session = requests.Session()

	def close(self):
		self.driver.close()

	def get(self, link):
		print("driver: fetching link: " + link)
		status = self.get_driver().get(link)
		print("driver: done fetching " + link)
		# time.sleep(20)
		return status

	def get_driver(self):
		return self.driver

	def open_chrome_browser(self):
		options = ChromeOptions()
		options.add_argument('--user-agent=""Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36""')
		options.add_argument('--no-sandbox')
		options.add_argument('--disable-dev-shm-usage')
		chrome_prefs = {}
		options.experimental_options["prefs"] = chrome_prefs
		chrome_prefs["profile.default_content_settings"] = {"images": 2}
		chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
		# options.add_argument('headless')
		path = f"{self.basedir}/data/chromedriver.exe"
		chrome = Chrome(executable_path=path, options=options)

		chrome.implicitly_wait(20)
		self.driver = chrome

	def close_browser(self):
		self.driver.close()

	def my_send_keys(self, element, value):
		for a in value:
			time.sleep(random.randint(1,100) / 1000)
			element.send_keys(a)

	def search_item(self, item_number):
		value = ''
		search_input = None
		is_done = False
		try:
			xpath = "input[data-id='myProductSearch']"
			search_input = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, xpath)))
			self.my_send_keys(search_input, item_number)
			is_done = True
		except Exception as e:
			print(f'cannot find search element {str(e)} for {item_number}')
		try:
			time.sleep(1)
			el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='virtualized-list']/div/div/div[contains(@class, 'price-col')]")))
			if el.text:
				value = el.text.split('\n')[0]
				print(f'==== found out value {value} for {item_number}')
		except Exception as e:
			print(f'cannot find price element {str(e)} for {item_number}')

		if search_input and is_done:
			search_input.clear()
		return value

	def read_datasheet(self):
		print(' ----- Read Sysco Sheet')
		self.wb = load_workbook(filename = self.sysco_path)
		self.sheet = self.wb['Sheet1']

	def save_close_datasheet(self):
		print('--- save and close sheet')
		try:
			self.wb.save(self.sysco_path)
			self.wb.close()
		except Exception as e:
			print(str(e))

	def run_request(self):
		match = requests.get('https://web-bff.shop.sysco.com/api/v1/products/map?order_from=1567182769401&order_to=1604075569401&view_id=2&view_type=SYSTEM_IPH')
		pdb.set_trace()

	def update_datasheet(self):
		print(' ----- Update Sysco Sheet')
		# search order item for price
		is_done = False
		for row in self.sheet.rows:
			for cell in row:
				if cell.column_letter == 'A' and cell.value:
					value = self.search_item(str(cell.value))
					time.sleep(1)
					if value:
						self.sheet[f'D{cell.row}'].value = value.replace('$', '')
						is_done = True

	def send_email(self):
		text = 'Finished the scraper'
		send_simple_email(text=text)

	def scrape_sysco(self):
		self.get('https://idmsupplier.cloud.sysco.com/shop/sps/auth?PartnerId=cxs-shop-prod')
		try:
			# login
			email_field = self.driver.find_element_by_xpath("//input[@id='email']")
			pwd_field = self.driver.find_element_by_xpath("//input[@id='password']")
			self.my_send_keys(email_field, SYSCO_USERNAME)
			self.my_send_keys(pwd_field, SYSCO_PASSWORD)
			pwd_field.send_keys(Keys.RETURN)

			time.sleep(16)

			# go to the list page
			self.get('https://shop.sysco.com/app/lists')
			self.session.get('https://shop.sysco.com/app/lists')
			time.sleep(3)
		except Exception as e:
			print(str(e))

	def run_sysco(self):
		self.read_datasheet()

		self.scrape_sysco()

		self.run_request()

		# self.update_datasheet()

		self.close_browser()

		self.save_close_datasheet()

		# self.send_email()

if __name__ == '__main__':
	Driver().run_sysco()


