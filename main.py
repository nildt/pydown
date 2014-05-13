#!/usr/bin/python

import urllib2
import re #regex
import os
import ConfigParser
import pycurl
import cStringIO
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
curl = pycurl.Curl()
for cmd in commands:
	curl.reset()
	curl.setopt(pycurl.VERBOSE, 0)
	curl.setopt(pycurl.FOLLOWLOCATION, 1);
	#setup authentification
	curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_ANY);
	curl.setopt(pycurl.USERPWD, cmd.login+":"+cmd.pssw);

	#Read res
	print ""
	print "Reading '" + cmd.url + "' ...",
	try:
		buf = cStringIO.StringIO()
		curl.setopt(pycurl.URL, cmd.url)
		curl.setopt(pycurl.WRITEFUNCTION, buf.write)
		curl.perform()
		html = buf.getvalue()
		
		#curl.unsetopt(pycurl.WRITEFUNCTION) bug??
		curl.reset()
		curl.setopt(pycurl.VERBOSE, 0)
		curl.setopt(pycurl.FOLLOWLOCATION, 1);
		#setup authentification
		curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_ANY);
		curl.setopt(pycurl.USERPWD, cmd.login+":"+cmd.pssw);
		#curl.setopt(pycurl.NOPROGRESS, 0)
		
		
		buf.close()
		print "OK"
		resRead += 1

		print "searching for regex '" + cmd.regex + "' :"
		p = re.compile(cmd.regex)
		matches = p.findall(html)
		if len(matches) == 0:
			print "Nothing found"

		if not os.path.isdir("./" + cmd.outDir):
			os.makedirs("./" + cmd.outDir)
	
		for match in matches:
			print "'" + match + "' ...",
			file_name = cmd.outDir + match.split('/')[-1]
			if not os.path.exists(file_name):
				f = None
				try:
					f = open(file_name, 'wb')
					curl.setopt(pycurl.URL, urljoin(cmd.url, match))
					curl.setopt(pycurl.FILE, f);
					curl.perform()
					print "OK"
					downloaded += 1
				except:
					print "failed"
					failed += 1
				finally:
					if not f is None:
						f.close()
			else:
				print "skipped"
				skipped += 1
	except:
		print "failed"
		resFailed += 1
curl.close()


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

