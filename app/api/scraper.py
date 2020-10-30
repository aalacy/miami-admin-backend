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
from pyvirtualdisplay import Display
import pdb

from app.email import send_simple_email, send_email_with_attachment_general
from app.util import encode_csv_data

SYSCO_USERNAME = 'cmdallm@gmail.com'
SYSCO_PASSWORD = 'UpworkTest1'
SYSCO_DATASHEET = '_Item List.xlsx'

CHENEY_USERNAME = 'cmdallm@gmail.com'
CHENEY_PASSWORD = 'cbi2644'

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
		Display(visible=0, size=(620, 840)).start()

		options = ChromeOptions()
		# options.add_argument('--user-agent=""Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36""')
		options.add_argument('--no-sandbox')
		# options.add_argument('--disable-dev-shm-usage')
		chrome_prefs = {}
		options.experimental_options["prefs"] = chrome_prefs
		chrome_prefs["profile.default_content_settings"] = {"images": 2}
		chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
		options.add_argument('headless')
		path = f"{self.basedir}/data/chromedriver"
		chrome = Chrome(options=options)

		chrome.implicitly_wait(20)
		self.driver = chrome

	def close_browser(self):
		self.driver.close()

	def my_send_keys(self, element, value):
		for a in value:
			time.sleep(random.randint(1,100) / 1000)
			element.send_keys(a)

	def find_sysco_item(self, item_number):
		value = ''
		el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='virtualized-list']/div/div/div[contains(@class, 'price-col')]")))
		if el.text:
			value = el.text.split('\n')[0]
			print(f'==== found out value {value} for {item_number}')

		return value

	def search_sysco_item(self, item_number):
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
			value = self.find_sysco_item(item_number)
		except Exception as e:
			try:
				value = self.find_sysco_item(item_number)
			except Exception as e:
				print(f'cannot find price element {str(e)} for {item_number}')

		if search_input and is_done:
			search_input.clear()
		return value

	def read_datasheet(self):
		print(' ----- Read Sheet')
		self.wb = load_workbook(filename = self.sysco_path)
		self.sheet = self.wb['Sheet1']

	def save_close_datasheet(self):
		print('--- save and close sheet')
		try:
			self.wb.save(self.sysco_path)
			self.wb.close()
		except Exception as e:
			print(str(e))

	def update_sysco_datasheet(self):
		print(' ----- Update Sysco Sheet')
		# search order item for price
		is_done = False
		cells = self.sheet['B1': 'C569']
		for c1, c2 in cells:
			if c1.value.strip() == 'Sysco' and c2.value:
				value = self.search_sysco_item(str(c2.value))
				time.sleep(1)
				if value:
					self.sheet[f'E{c2.row}'].value = value.replace('$', '')
					
		# for row in self.sheet.rows:
		# 	for cell in row:
		# 		if cell.column_letter == 'A' and cell.value:
		# 			value = self.search_item(str(cell.value))
		# 			time.sleep(1)
		# 			if value:
		# 				self.sheet[f'D{cell.row}'].value = value.replace('$', '')
		# 				is_done = True

	def send_email(self):
		text = 'Finished the scraper. \n Please check the following url to download the excel file \n http://100.25.17.56/api/static/download'
		send_simple_email(text=text)
		# b64data = [encode_csv_data(self.sysco_path, 'Item List')]
		# html_content = '<strong>Here is the xlxs attachment after run scrapers</strong>'
		# send_email_with_attachment_general(data=b64data, html=html_content, to_email='ideveloper003@gmail.com')
		

	def scrape_sysco(self):
		self.get('https://idmsupplier.cloud.sysco.com/shop/sps/auth?PartnerId=cxs-shop-prod')
		try:
			# login
			email_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
			pwd_field = self.driver.find_element_by_id("password")
			self.my_send_keys(email_field, SYSCO_USERNAME)
			self.my_send_keys(pwd_field, SYSCO_PASSWORD)
			pwd_field.send_keys(Keys.RETURN)

			time.sleep(10)

			# go to the list page
			self.get('https://shop.sysco.com/app/lists')
			self.get('https://shop.sysco.com/app/lists')
			time.sleep(23)
		except Exception as e:
			print(str(e))

	def run_scraper(self):
		self.run_sysco()

		self.run_cheney()

	def run_sysco(self):
		self.read_datasheet()

		self.scrape_sysco()

		self.update_sysco_datasheet()

		self.close_browser()

		self.save_close_datasheet()

	def scrape_cheney(self):
		self.driver.get('https://www.cheneycentral.com/Web/#/home')
		time.sleep(10)
		try:
			# login
			login_btn = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//a[@class='btn btn-login']")))
			login_btn.click()
			time.sleep(1)
			email_field = self.driver.find_element_by_xpath('//input[@placeholder="Email"]')
			pwd_field = self.driver.find_element_by_xpath('//input[@placeholder="Password"]')
			self.my_send_keys(email_field, CHENEY_USERNAME)
			self.my_send_keys(pwd_field, CHENEY_PASSWORD)
			pwd_field.send_keys(Keys.RETURN)

			time.sleep(20)

			# go to the list page
			self.get('https://www.cheneycentral.com/Web/#/itembook')
			time.sleep(13)
		except Exception as e:
			print(str(e))

	def update_cheney_datasheet(self):
		print(' ----- Update Sheet')
		# search order item for price
		is_done = False
		cells = self.sheet['B1': 'C569']
		for c1, c2 in cells:
			if c1.value.strip() == 'Cheney' and c2.value:
				value = self.search_cheney_item(str(c2.value))
				time.sleep(1)
				if value:
					self.sheet[f'E{c2.row}'].value = value.replace('$', '')

	def find_cheney_item(self, item_number):
		value = ''
		el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'table-list')]/tbody/tr/td[6]")))
		if el.text:
			value = el.text.split('\n')[0]
			print(f'==== found out value {value} for {item_number}')

		return value

	def search_cheney_item(self, item_number):
		value = ''
		search_input = None
		is_done = False
		try:
			search_input = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, 'searchbox')))
			self.my_send_keys(search_input, item_number)
			search_input.send_keys(Keys.RETURN)
			is_done = True
		except Exception as e:
			print(f'[cheney] cannot find search element {str(e)} for {item_number}')
	
		try:
			time.sleep(2)
			value = self.find_cheney_item(item_number)
		except Exception as e:
			try:
				value = self.find_cheney_item(item_number)
			except Exception as e:
				print(f'[cheney] cannot find price element {str(e)} for {item_number}')

		# if search_input and is_done:
		# 	search_input.clear()
		return value


	def run_cheney(self):
		self.read_datasheet()

		self.scrape_cheney()

		self.update_cheney_datasheet()

		self.close_browser()

		self.save_close_datasheet()

		self.send_email()

if __name__ == '__main__':
	# Driver().run_sysco()
	Driver().send_email()


