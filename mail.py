import mysql.connector
import re
import requests
import urllib.parse
from datetime import datetime
import imaplib
from email.parser import BytesParser
from email.utils import getaddresses
import AI
import jsParser
from pynotifier import Notification
import platform
from plyer import notification
from urllib.parse import urlparse
import pickle
import numpy
import yandex_search
from bs4 import BeautifulSoup

MAILS_TO_CACHE = 5

SKIP = ["facebook.com","w3.org"]
class Logger:
	def __init__(self, filename):
		self.file = open(filename, "a+")

	def error(self, msg: str):
		self.file.write("[ERROR] " + self.generate_log(msg))
		self.file.flush()

	def debug(self, msg):
		self.file.write("[DEBUG] " + self.generate_log(msg))
		self.file.flush()

	def info(self, msg: str):
		self.file.write("[INFO] " + self.generate_log(msg))
		self.file.flush()

	def generate_log(self, msg: str):
		now = datetime.now()
		timestamp = now.strftime("%b %d %Y %H:%M:%S")
		return timestamp + " : " + msg + "\n"

	def stop(self):
		self.file.close()


class MailBox:

	def __init__(self, email: str, passwd: str, server: str, port: int, mysql_creds: dict, sensitivity: int,
				 threshold: int, logger: Logger):
		try:
			self.log = logger
			self.log.info("Started MailBox listener for " + email)
			self.FROM_EMAIL = email
			self.FROM_PWD = passwd
			self.SMTP_SERVER = server
			self.SMTP_PORT = port
			self.imap = imaplib.IMAP4_SSL(self.SMTP_SERVER, self.SMTP_PORT)
			self.imap.login(self.FROM_EMAIL, self.FROM_PWD)
			self.imap.select('INBOX')
			self.mysql_creds = mysql_creds
			self.threshold = threshold
			self.sensitivity = sensitivity
			self.get_ids()
			# The mails dictionary format it <mail_id>:(<Mail_Object>,<Modified time>)
			self.mails = {}
			self.mysql = mysql_creds
			self.spam_folder = self.detect_spam_folder()
			self.get_new_mails()
		except Exception as e:
			self.log.error(str(e))

	def get_ids(self):
		try:
			self.imap.select("INBOX", False)
			typ, ids = self.imap.uid('search', None, 'ALL')
			self.ids = ids[0].decode().split()
			self.log.debug(str(self.ids))
		except Exception as e:
			self.log.error(str(e))
			self.imap = imaplib.IMAP4_SSL(self.SMTP_SERVER, self.SMTP_PORT)
			self.imap.login(self.ORG_EMAIL, self.FROM_PWD)
			self.imap.select('INBOX', False)
			self.get_ids()

	def get_new_mails(self):
		mysql_db = mysql.connector.connect(
				user=self.mysql_creds["mysql_username"],
				password=self.mysql_creds["mysql_password"],
				database=self.mysql_creds["mysql_database"],
				host=self.mysql_creds["mysql_host"]
		)
		cursor = mysql_db.cursor()
		while len(self.mails) <= MAILS_TO_CACHE:
			id = self.ids[-1 - len(self.mails)]
			cursor.execute(
				"SELECT mail_id FROM logs WHERE mail_id = '{}' AND account = '{}'".format(id, self.FROM_EMAIL))
			cursor.fetchall()
			if cursor.rowcount > 0:
				self.mails[id] = "[BUFFERED MAIL]"
				continue
			typ, messageRaw = self.imap.uid('fetch', id, '(RFC822)')
			self.log.info("Found mail with id: " + str(id))
			email = messageRaw[0][1]
			self.mails[id] = Mail(email, self.mysql_creds, self.threshold, self.sensitivity, self.FROM_EMAIL, self.log,
								  id, self.spam_folder)
			self.mails[id].check_spam()
			self.log.info("Checked new mail with id: " + str(id))

	def refresh_new_mails(self):
		self.log.info("Refreshing mails")
		old_ids = self.ids
		self.get_ids()
		#self.log.debug(str(self.ids))
		diff_ids = set(self.ids) - set(old_ids)
		for id in diff_ids:
			self.log.info("Found new mail with id: " + str(id))
			typ, messageRaw = self.imap.uid('fetch', id, '(RFC822)')
			self.log.info("Fetched the new mail")
			email = messageRaw[0][1]
			self.mails[id] = Mail(email, self.mysql_creds, self.threshold, self.sensitivity, self.FROM_EMAIL, self.log,
								  id, self.spam_folder)
			self.mails[id].check_spam()

	def check_spam(self):
		for mail_name in self.mails:
			mail_obj = self.mails[mail_name]
			mail_obj.check_spam()
			self.log.info("Checked new mail with id: " + str(mail_name))
			if mail_obj.get_spam() == 1:
				self.log.info("Found spam mail sent by: " + mail_obj.header_data["From"].split("<")[1][:-1])
				result = self.imap.uid('COPY', mail_obj.mail_id, mail_obj.spam_folder)
				if result[0] == 'OK':
					mov, data = self.imap.uid('STORE', mail_obj.mail_id, '+FLAGS', '(\Deleted)')
					self.imap.expunge()

	def detect_spam_folder(self):
		folder = ""
		for i in self.imap.list()[1]:
			l = i.decode().split(' "/" ')
			if "Junk" in l[0]:
				folder = l[1]
				break
			if "Trash" in l[0]:
				folder = l[1]
		if folder[0] == "\"":
			folder = folder[1:]
		if folder[-1] == "\"":
			folder = folder[:-1]
		return folder


class Mail:

	def __init__(self, mail_data, mysql_creds, threshold, sensitivity, account, logger, mail_id, spam_folder):
		self.JS_IMPORT_REGEX = r'/<script.*(?:src="(.*)").*>/s'
		self.JS_EXTRACT_REGEX = r'/<script.*>(.*?)<\/script>/s'
		self.URL_REGEX = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|[^\x00-\x7F]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
		self.parser = BytesParser()
		self.sensitivity = sensitivity
		self.threshold = threshold
		self.log = logger
		self.spam_folder = spam_folder
		self.mysql_db = mysql.connector.connect(
				user=mysql_creds["mysql_username"],
				password=mysql_creds["mysql_password"],
				database=mysql_creds["mysql_database"],
				host=mysql_creds["mysql_host"]
		)
		self.account = account
		self.spam_points = 0
		self.js_code = {}
		self.urls_in_document = []
		self.documents = {}
		self.mail_id = mail_id
		# The headers are defined as <key>:<to_remove_from key>
		# -1 is used to define the last header, after that comes the mail contents
		self.whitelisted = False
		self.blacklisted = False
		self.parsed_mail = self.parser.parsebytes(mail_data)
		self.header_data = dict(self.parsed_mail)
		self.message = ""
		self.extract_message()
		self._spam = -1
		self.check_whitelist()
		self.check_blacklisted()
		self.urls = re.findall(self.URL_REGEX, self.message)
		for i in range(len(self.urls)):
			self.urls[i] = self.urls[i].strip()

	def add_domain_to_blacklist(self,url):
		domain = urlparse(url).hostname
		cursor = self.mysql_db.cursor()
		cursor.execute("INSERT INTO new_blacklists(domain) VALUES('{}')".format(domain.encode("idna").decode("utf-8")))
		cursor.execute("INSERT INTO domain_blacklist(domain) VALUES('{}')".format(domain.encode("idna").decode("utf-8")))

	def extract_message(self):
		if self.parsed_mail.is_multipart():
			for i in self.parsed_mail.get_payload():
				payload = i.get_payload(decode=True)
				try:
					self.message += payload.decode("utf-8")
				except AttributeError as e:
					self.log.error("AttributeError while trying to get message from mail with id " + str(self.mail_id))
					print(e)
				except UnicodeDecodeError as e:
					self.log.error(
						"UnicodeDecodeError while trying to get message from mail with id " + str(self.mail_id))
					print(e)
		else:
			payload = self.parsed_mail.get_payload(decode=True)
			try:
				self.message += payload.decode("utf-8")
			except AttributeError as e:
				self.log.error("AttributeError while trying to get message from mail with id " + str(self.mail_id))
				print(e)
			except UnicodeDecodeError as e:
				self.log.error("UnicodeDecodeError while trying to get message from mail with id " + str(self.mail_id))
				print(e)

	def check_blacklisted(self, url=None):
		if url != None:
			url = url.encode("idna").decode("utf-8")
		cursor = self.mysql_db.cursor()
		if not url == None:
			cursor.execute("SELECT * FROM domain_blacklist WHERE domain LIKE '{}';".format(url))
			cursor.fetchall()
			if cursor.rowcount > 0:
				cursor.close()
				return True
			return False
		mail_header = self.header_data["From"].split("<")[1][:-1]
		mail = mail_header
		cursor.execute("SELECT * FROM mail_blacklist WHERE mail='{}';".format(mail))
		cursor.fetchall()
		if cursor.rowcount >= 1:
			print("Blacklisted")
			self.blacklisted = True

	def check_whitelist(self, url=None):
		if url != None:
			url = url.encode("idna").decode("utf-8")
		cursor = self.mysql_db.cursor()
		if not url == None:
			cursor.execute("SELECT * FROM domain_whitelist WHERE domain LIKE '%{}%';".format(url))
			cursor.fetchall()
			if cursor.rowcount > 0:
				cursor.close()
				return True
			return False
		mail_header = self.header_data["From"].split("<")[1][:-1]
		mail = mail_header
		cursor.execute("SELECT * FROM mail_whitelist WHERE mail='{}';".format(mail))
		cursor.fetchall()
		if cursor.rowcount >= 1:
			self.whitelisted = True

	def check_special_chars(self):
		for url in self.urls:
			parsed = urllib.parse.urlparse(url.encode("idna").decode("utf-8").encode("utf-8").decode("idna"))
			special_char_count = 0
			for char in parsed.netloc:
				if not char == ".":
					if not char.encode("utf-8") == char.encode("idna"):
						print("Special char detected")
						self._spam = 1

	def aiPredict(self,data):
		with open("aiModel","rb") as m:
			aiModel = pickle.load(m)
			ai_in = (data["dir_num"], data["index_num"], data["length"], data["out_resources"], data["robots_entries"], data["special_char_num"], data["subdomain_len"], data["subdomain_num"], data["tld_trust"])
			return aiModel.predict(numpy.reshape(ai_in,(1, 9)))

	def find_list_resources (self,tag, attribute,soup):
		list = []
		for x in soup.findAll(tag):
			try:
				list.append(x[attribute])
			except KeyError:
				pass
		return(list)

	def get_url_data(self,url,yandex,timeout=30):
		data = {}
		data["length"] = (len(url.split("://")[1].split("?")[0]))
		data["dir_num"] = (url.find("/")-2)
		parsed = urlparse(url.encode("idna").decode("utf-8").encode("utf-8").decode("idna"))
		hostname_split = parsed.hostname.split(".")
		data["tld_trust"] = int(hostname_split[-1].lower() in ["com", "org", "net"])
		data["subdomain_num"] = len(hostname_split) - 2
		data["subdomain_len"] = len("".join(hostname_split[:-2]))
		special_char_count = 0
		for char in parsed.hostname:
			if char == ".":
				continue
			if not char.encode("utf-8") == char.encode("idna"):
				special_char_count += 1
		data["special_char_num"] = special_char_count
		#Advanced data extraction
		try:
			data["index_num"] = int(yandex.search("site:{}".format(parsed.hostname)).found["all"])
		except yandex_search.NoResultsException:
			data["index_num"] = 0
		robot_entry_counter = 0
		try:
			response = requests.get("{}://{}/robots.txt".format(parsed.scheme, parsed.netloc), allow_redirects=True, verify=False, timeout=timeout)
			if response.status_code == 200:
				lines = response.text.split("\n")
				lines = [x for x in lines if x != ""]
				robot_entry_counter += len([x for x in lines if x[0] != "#"])
			else:
				pass
		except Exception as e:
			print(e)
		data["robots_entries"] = robot_entry_counter
		try:
			req = requests.get(url, verify=False, timeout=timeout)
			if req.status_code == 200:
				soup = BeautifulSoup(req.text,'html.parser')
				image_scr = self.find_list_resources('img',"src",soup)
				script_src = self.find_list_resources('script',"src",soup)
				css_link = self.find_list_resources("link","href",soup)
				all_links = image_scr + css_link + script_src
				out_links = []
				for link in all_links:
					parsed_link = urlparse(link)
					if parsed_link.hostname != parsed.hostname:
						out_links.append(link)
				data["out_resources"] = len(out_links)
			else:
				data["out_resources"] = -1
		except Exception as e:
			print(e)
			data["out_resources"] = -1
		return data

	def check_url(self, url):
		yandex = yandex_search.Yandex(api_user='raporcubaba@gmail.com', api_key='03.1042294429:b8e679f9acadef49ebab0d9726ccef58')
		data = self.get_url_data(url,yandex,timeout=10)
		if self.aiPredict(data):
			self.add_domain_to_blacklist(url)
			self.spam_points += self.sensitivity

	def check_js(self):
		for url in self.js_code:
			for js in self.js_code[url]:
				if self.check_blacklisted(url=js):
					self._spam = 1
				if self.check_js_code(self.js_code[js]):
					self.add_domain_to_blacklist(url)
					self.spam_points += self.sensitivity

	def check_disallowed_chars(self, url_start, chars=["<", ">", "'", "\""]):
		url = url_start
		for char in chars:
			if char in url:
				return True
			if urllib.parse.quote_plus(char) in url:
				return True
			if urllib.parse.quote_plus(urllib.parse.quote_plus(char)) in url:
				return True
		return False

	def check_tld(self,url):
		if urlparse(url).hostname.split(".")[-1] in ["info","tk","gq"]:
			self._spam = 1

	def check_domain_name(self,url):
		pass # TODO fill this up

	def discover_url(self,urls):
		for url in urls:
			foo = False
			for i in self.documents:
				if urlparse(url).hostname == urlparse(i).hostname:
					foo = True
			if foo:
				continue
			while 1:
				if self.check_whitelist(url=url):
					break
				if self.check_blacklisted(url=url):
					self._spam = 1
					return
				self.log.info(url)
				self.check_disallowed_chars(url)
				self.keyword_search(url)
				self.check_xss(url)
				self.check_url(url)
				self.check_tld(url)
				self.check_domain_name(url)
				try:
					r = requests.get(url, allow_redirects=False)
				except requests.exceptions.ConnectionError:
					break
				#detect all status codes in the format 3xx
				try:
					self.documents[url] = r.content.decode()
					for i in self.extract_urls(self.documents[url]):
						foo = False
						for i in self.documents:
							if urlparse(url).hostname == urlparse(i).hostname:
								foo = True
						if foo:
							continue
						skip = False
						for j in SKIP:
							if j in i:
								skip = True
						if skip:
							continue
						foo = []
						foo.append(i.strip())
						self.discover_url(foo)
				except UnicodeDecodeError:
					pass
				if r.status_code == 302 or r.status_code == 303:
					location = r.headers["location"]
					if location.startswith("http"):
						url = location
					else:
						url = "/".join(url.split("/")[:-1]) + location
					continue
				else:
					break

	def keyword_search(self, url):
		keywords = self.mysql_db.cursor()
		keywords.execute("SELECT * FROM keywordlist;")
		result = keywords.fetchall()
		for row in result:
			if row[0] in url:
				if  ".".join(urlparse(url).hostname.split(".")[-2:]) != row[1]:
					self._spam = 1

	def check_xss(self, url):
		malicious = self.check_disallowed_chars(url)
		if malicious:
			print("ADDED SPAM POINTS")
			self.spam_points += self.sensitivity

	#TODO add deobfuscation
	def extract_javascript(self): #TODO not working
		p = re.compile(self.JS_IMPORT_REGEX)
		for doc in self.documents:
			self.js_code[doc] = []
			for url in p.findall(self.documents[doc]):
				r = requests.get(url, allow_redirects=False)
				if r.status_code == 200:
					self.js_code[doc].append(r.content)
			p = re.compile(self.JS_EXTRACT_REGEX)
			for js in p.findall(doc):
				if js != "":
					self.js_code[doc].append(js)

	def extract_urls(self, doc): # Extract URLs from the documents and save them to the array urls_in_document
		p = re.compile(self.URL_REGEX)
		res = p.findall(doc)
		return res

	def check_stored_xss(self):
		self.extract_javascript()
		for url in self.js_code:
			url_spam_count = 0
			for js in self.js_code[url]:
				if url_spam_count > 6:
					self.add_domain_to_blacklist(url)
				if self.check_blacklisted(url=url):
					self._spam = 1
					return
				if self.check_js_code(js):
					url_spam_count += 3
					self.spam_points += self.sensitivity

	def check_js_code(self, code):
		parsedJs = jsParser.parseJavascript(code, False)
		return AI.aiPredict(parsedJs)

	def log_mail(self):
		cursor = self.mysql_db.cursor()
		domain = getaddresses(self.parsed_mail.get_all('from', []))[0][1]
		cursor.execute(
			"INSERT INTO logs (sender_domain,result, account, mail_id) VALUES ('{}','{}','{}','{}')".format(domain,
																											self.get_spam(),
																											self.account,
																											self.mail_id))
		self.mysql_db.commit()
		cursor.close()

	def check_spam(self):
		if self.whitelisted:
			self._spam = 0
			self.log_mail()
			return
		elif self.blacklisted:
			self._spam = 1
		else:
			self.discover_url(self.urls)

			self.check_stored_xss()
			if self.threshold < self.spam_points:
				self._spam = 1
		if self.get_spam() == 1:
			self.log.info("Mail moved to spam with id: " + str(self.mail_id))
			if platform.system() == "Windows":
				notification.notify(
						title='Found spam mail by: ' + getaddresses(self.parsed_mail.get_all('from', []))[0][1],
						message=self.account,
						app_icon=None,
						timeout=10, )
			else:
				Notification(
						title='Found spam mail by: ' + getaddresses(self.parsed_mail.get_all('from', []))[0][1],
						description=self.account,
						duration=10,
						urgency=Notification.URGENCY_CRITICAL
				).send()
		self.log_mail()

	def get_spam(self) -> int:
		if self.whitelisted:
			return 0
		return self._spam