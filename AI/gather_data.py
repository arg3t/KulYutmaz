import pandas as pd
import os
import urllib.request
from datetime import datetime
from progressbar import ProgressBar
import requests
import yandex_search
from urllib.parse import urlparse, quote
import requests, json
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TRUSTED_TLDS = ["com", "org", "net"]
pbar = None
downloaded = 0


def show_progress(count, block_size, total_size):
	global pbar
	global downloaded
	if pbar is None:
		pbar = ProgressBar(maxval=total_size)

	downloaded += block_size
	pbar.update(block_size)
	if downloaded == total_size:
		pbar.finish()
		pbar = None
		downloaded = 0


def get_data(phishtank_key, force_update=False):
	if not os.path.isfile("phishtank.csv") or force_update:
		urllib.request.urlretrieve("http://data.phishtank.com/data/{}/online-valid.csv".format(phishtank_key),
								   "phishtank.csv", show_progress)
	if not os.path.isfile("common.csv") or force_update:
		data = {"url":[]}
		with open("keywordList") as wordlist:
			keywords = wordlist.read().split("\n")
			wordlist.close()
		suggestions = []
		for word in keywords:
			URL = ("http://suggestqueries.google.com/complete/search?client=firefox&q="+word)
			headers = {'User-agent':'Mozilla/5.0'}
			response = requests.get(URL, headers=headers)
			result = json.loads(response.content.decode('utf-8'))
			for r in result[1]:
				suggestions.append(r)
		yandex = yandex_search.Yandex(api_user='yksiber', api_key='03.1041007756:28d93f7d79ff3c91b861da63e38a8e5c')
		for word in suggestions:
			top10 = (yandex.search(word).items[0:10])
			for site in top10:
				data["url"].append(site)
		common = pd.DataFrame(data)
		common.to_csv("common.csv")
	urls = (pd.read_csv("phishtank.csv"), pd.read_csv("common.csv"))
	return urls

def find_list_resources (tag, attribute,soup):
	list = []
	for x in soup.findAll(tag):
		try:
			list.append(x[attribute])
		except KeyError:
			pass
	return(list)

def get_url_data(url,yandex,timeout=30):
	#Basic data extraction
	data = {}
	data["length"] = (len(url.split("://")[1].split("?")[0]))
	data["dir_num"] = (url.find("/")-2)
	parsed = urlparse(url)
	hostname_split = parsed.hostname.split(".")
	data["tld_trust"] = int(hostname_split[-1].lower() in TRUSTED_TLDS)
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
		data["index_num"] = yandex.search("site:{}".format(parsed.hostname)).found["all"]
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
			image_scr = find_list_resources('img',"src",soup)
			script_src = find_list_resources('script',"src",soup)
			css_link = find_list_resources("link","href",soup)
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
	data["url"] = url
	return data


def extract_data(raw_data, force_update=False):
	reps = 0
	phishing, benign = raw_data[0], raw_data[1]
	data = {
		"phishing": [],
		"length": [],
		"out_resources": [],
		"dir_num": [],
		"special_char_num": [],
		"robots_entries": [],
		"tld_trust": [],
		"index_num": [],
		"subdomain_len": [],
		"subdomain_num": [],
		"url": []
	}
	if not os.path.isfile("dataset.csv") or force_update:
		largest_dataset = 0
		while os.path.isfile(largest_dataset + 300):
			largest_dataset += 300
		try:
			# filter old sites
			old = []
			for index, row in phishing.iterrows():
				date = datetime.strptime(row["submission_time"],"%Y-%m-%dT%H:%M:%S+00:00")
				if date.year < 2020:
					old.append(index)
			phishing = phishing.drop(old)
			yandex = yandex_search.Yandex(api_user='yksiber', api_key='03.1041007756:28d93f7d79ff3c91b861da63e38a8e5c')
			for index, row in phishing.iterrows():
				reps += 1
				if reps < largest_dataset:
					continue
				if reps % 300 == 0:
					pd.DataFrame(data).to_csv("dataset{}.csv".format(reps))
				url = row['url']
				print("[INFO]: {} : {}".format(reps, url))
				url_data = get_url_data(url, yandex)
				data["phishing"].append(1)
				data["length"].append(url_data["length"])
				data["dir_num"].append(url_data["dir_num"])
				data["special_char_num"].append(url_data["special_char_num"])
				data["tld_trust"].append(url_data["tld_trust"])
				data["index_num"].append(url_data["index_num"])
				data["subdomain_len"].append(url_data["subdomain_len"])
				data["subdomain_num"].append(url_data["subdomain_num"])
				data["out_resources"].append(url_data["out_resources"])
				data["robots_entries"].append(url_data["robots_entries"])
				data["url"].append(url_data["url"])
			for index, row in benign.iterrows():
				reps += 1
				if reps < largest_dataset:
					continue
				if reps % 300 == 0:
					pd.DataFrame(data).to_csv("dataset{}.csv".format(reps))
				url = row['url']
				print("[INFO]: {} : {}".format(reps, url))
				url_data = get_url_data(url, yandex)
				data["phishing"].append(1)
				data["length"].append(url_data["length"])
				data["dir_num"].append(url_data["dir_num"])
				data["special_char_num"].append(url_data["special_char_num"])
				data["tld_trust"].append(url_data["tld_trust"])
				data["index_num"].append(url_data["index_num"])
				data["subdomain_len"].append(url_data["subdomain_len"])
				data["subdomain_num"].append(url_data["subdomain_num"])
				data["out_resources"].append(url_data["out_resources"])
				data["robots_entries"].append(url_data["robots_entries"])
				data["url"].append(url_data["url"])
			pd.DataFrame(data).to_csv("dataset.csv".format(reps))
		except Exception as e:
			print("[ERROR]: {}".format(e))
	return pd.read_csv("dataset.csv")


raw_data = get_data("01115eebdbf465734c08fedb2e4d93f414d1a31fa10bfcb248d0f75071e156ff")
print("DOWNLOAD COMPLETED!")
dataset = extract_data(raw_data)
print("EXTRACT COMPLETED!")
