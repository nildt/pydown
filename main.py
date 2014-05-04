#!/usr/bin/python

import urllib2
import re #regex
import os
import ConfigParser
from urlparse import urlparse, urlsplit, urljoin

class Command:
	#input
	url = ""
	regex = ""
	outDir = ""
	login = ""
	pssw = ""
	
def get(config, section, option, default=None):
	try:
		return config.get(section, option)
	except:
		return default
	
#Read ./config.ini
print "Reading ./config.ini ...",
config = ConfigParser.ConfigParser()
config.read("./config.ini");
print "OK"

commands = []

#Parse ./config.ini
print "Parsing ./config.ini :"
for section in config.sections():
	print "Found section '"+section+"'"
	cmd = Command()
	cmd.url           = get(config, section, "url")
	cmd.regex         = get(config, section, "regex")
	cmd.outDir        = get(config, section, "outDir", "./")
	if get(config, section, "askAuth") != "true":
		cmd.login         = get(config, section, "login",  "")
		cmd.pssw          = get(config, section, "pssw",   "")
	else:
		print "  login: ",
		cmd.login = raw_input()
		print "  pssw:  ",
		cmd.pssw  = raw_input()
	commands.append(cmd)
print "Done"

#stats
resRead   = 0
resFailed = 0

downloaded = 0
skipped    = 0
failed     = 0
	
#read commands
for cmd in commands:
	#setup authentification
	password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	password_mgr.add_password(None, urlparse(cmd.url).netloc, cmd.login, cmd.pssw)

	handler = urllib2.HTTPBasicAuthHandler(password_mgr)
	opener = urllib2.build_opener(urllib2.HTTPHandler, handler)

	#Read res
	print ""
	print "Reading '" + cmd.url + "' ...",
	try:
		response = opener.open(cmd.url)
		html = response.read()
		print "OK"
		resRead += 1

		print "searching for regex '" + cmd.regex + "' :"
		p = re.compile(cmd.regex)
		matches = p.findall(html)
		if len(matches) == 0:
			print "Nothing found"

		if not os.path.isdir("./" + cmd.outDir):
			os.mkdir("./" + cmd.outDir)
	
		for match in matches:
			print "'" + match + "' ...",
			file_name = cmd.outDir + match.split('/')[-1]
			if not os.path.exists(file_name):
				try:
					data = opener.open(urljoin(cmd.url, match)).read()
					f = open(file_name, 'wb')
					f.write(data)
					f.close()
					print "OK"
					downloaded += 1
				except:
					print "failed"
					failed += 1
			else:
				print "skipped"
				skipped += 1
	except:
		print "failed"
		resFailed += 1


print "";
print "Resources:";
print "  read:   %d" % (resRead,);
print "  failed: %d" % (resFailed,);
print "Files:"
print "  downloaded: %d" % (downloaded,);
print "  skipped:    %d" % (skipped,);
print "  failed:     %d" % (failed,);
if resFailed + failed == 0:
	print "Success";
else:
	print "Errors occured";

