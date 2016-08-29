import requests
import math
from bs4 import BeautifulSoup as bs
from time import time
import argparse
import os
import getpass
import re

MODULE_WEBPAGE_URL = "http://www-module.cs.york.ac.uk"
ITS_YORK_LOGIN = "https://www.cs.york.ac.uk/login-its/login.php"
ITS_ACCESS_COOKIE = "ITSaccess"

current_cookie = {
	ITS_ACCESS_COOKIE : ""
}

login_parameters = {
	"login_time":math.floor(time()),
	"itsaccess_login_mode":"login",
	"login_reason":"you have not logged in",
	"login_url":MODULE_WEBPAGE_URL,
	"userdb": "",
	"username": "",
	"password":""
}

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Script to download all PDFs from York CS module webpages")
	parser.add_argument("username", type=str, help="Your York username e.g. aa1234")
	parser.add_argument("selected_modules", nargs="+", help="The abbreviations of the modules to download")
	parser.add_argument("path",type=str, help="The location to download files in directory structure e.g. /Users/username/Documents ")
	args = parser.parse_args()

	login_parameters["password"] = getpass.getpass()
	login_parameters["username"] = args.username;
	print("Getting PDFs for modules %s as user %s" % (args.selected_modules, args.username))

	try:
		print("Fetching ITSAccess cookie from %s" % ITS_YORK_LOGIN)
		r = requests.post(ITS_YORK_LOGIN, data = login_parameters)
		if "failed" in r.text:
			print("Failed to authenticate at %s" % ITS_YORK_LOGIN)
			print("Aborting")
			exit(1)

		print("Received ITSAccess cookie with value %s" % r.cookies[ITS_ACCESS_COOKIE])
		current_cookie[ITS_ACCESS_COOKIE] = r.cookies[ITS_ACCESS_COOKIE]

		for module_name in args.selected_modules:
			module_name = module_name.lower()
			r = requests.get(MODULE_WEBPAGE_URL + "/" + module_name.lower(),cookies=current_cookie)
			if not os.path.exists(args.path + '/' + module_name.lower()):
				os.makedirs(args.path + '/' + module_name.lower())
			soup = bs(r.text, "html.parser")
			all_a_tags = soup.find_all('a')
			pdf_a_tags = [a for a in all_a_tags if a.has_attr('href') and "pdf" in a["href"]]

			for element in pdf_a_tags:
				filename = args.path + '/' + module_name.lower() + '/' + element["href"].split("/")[-1]
				print filename
				with open(filename, "wb") as handle:
					print("Getting " + MODULE_WEBPAGE_URL + "/" + module_name.lower() + "/" + element["href"])
					pattern = re.compile(r"(http://|https://).*")
					if(pattern.match(element["href"])):
						dl = requests.get(element["href"], stream=True, cookies=current_cookie)
					else:
						dl = requests.get(MODULE_WEBPAGE_URL + "/" + module_name.lower() + "/" + element["href"], stream=True, cookies=current_cookie)
					if not dl.ok:
						print(filename + " failed to download, continuing...\n")
						continue

					for block in dl.iter_content(1024):
							handle.write(block)
					print("Created %s" % filename + "\n")

	except Exception as e:
		import traceback
		print("Hit exception, exiting")
		print(e)
		traceback.print_exc()
