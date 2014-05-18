#!/usr/bin/python
#coding: utf

import urllib2
import re #regex
import os
import ConfigParser
import pycurl
import cStringIO
from urlparse import urlparse, urlsplit, urljoin

# Stores the configparameters
class Command:
	#input
	url = ""
	regex = ""
	outDir = ""
	login = ""
	pssw = ""
	ilias = ""

def logoutilias(curl):
	curl.setopt(pycurl.URL, "https://ilias3.uni-stuttgart.de/logout.php?lang=de")
	curl.setopt(pycurl.VERBOSE, 0)
	curl.setopt(pycurl.FOLLOWLOCATION, 1) 
	buf = cStringIO.StringIO()
	curl.setopt(pycurl.WRITEFUNCTION, buf.write)
	curl.perform()
	buf.close()
	print "[+]    Logged out!!"
	if os.path.exists(cookie):
			open(cookie, 'w').close()
			print "[+]    Cookie deleted!"
	else:
		print "[-]    Couldn't delete Cookie"

def loadHtml(curl, url):
	buf = cStringIO.StringIO()
	#curl.setopt(pycurl.COOKIEFILE,"iliascookie.txt" )
	curl.setopt(pycurl.URL, url)
	curl.setopt(pycurl.WRITEFUNCTION, buf.write)
	curl.setopt(pycurl.VERBOSE, 0)
	curl.setopt(pycurl.FOLLOWLOCATION, 1) 
	curl.perform()
	html = buf.getvalue()
	#print html
	buf.close()
	print "[+]    Loaded html"
	return html

# If rekursion multiregex needed
def findLinks(url, regex, curl):
	if len(regex) == 0:
		print "[-]    Regex seems to be zero..."
		return []
	print "[+]    loading url'" + url + "'"
	html = loadHtml(curl, url)
	print "[+]    searching for regex '" + regex[0] + "' :"
	p = re.compile(regex[0])
	matches = p.findall(html)
	links = []
	if len(regex) == 1:#last regex
		for match in matches:
			links.append(urljoin(url, match))
			print links
	else: 
		for match in matches:
			print match
			site = urljoin(url, match)
			links.extend(findLinks(site, regex[1:], curl));
	return links

# Will set ilias cookie
def loginilias(cmd):
	# Here the cookie is saved
	cookie = 'iliascookie.txt'
	print "[+]    Entered ilias"
	c = pycurl.Curl()
	# Standartloginpage
	data = "password=" + cmd.pssw + "&" + "username=" + cmd.login
	c.setopt(c.URL, "https://ilias3.uni-stuttgart.de/login.php?target=&soap_pw=&ext_uid=&cookies=nocookies&client_id=Uni_Stuttgart&lang=de")
	c.setopt(c.POST,1)
	c.setopt(c.POSTFIELDS, data)
#	c.setopt(pycurl.CONNECTTIMEOUT, 5) Braucht man das?
#	c.setopt(pycurl.TIMEOUT, 8)
	c.setopt(c.FOLLOWLOCATION, 1)
	# No output: https://stackoverflow.com/questions/7668141/pycurl-keeps-printing-in-terminal
	c.setopt(pycurl.WRITEFUNCTION, lambda x: None)
	# Save cookie!
	pycurl.COOKIESESSION = 96
	c.setopt(pycurl.COOKIESESSION, True);
	c.setopt(c.COOKIEJAR, cookie)
	#c.setopt(c.SSL_VERIFYPEER, 0);
	c.setopt(c.FAILONERROR, True)
	# Don't need to know everything
	c.setopt(pycurl.VERBOSE,0)
	c.setopt(pycurl.HTTPHEADER, ["Host: ilias3.uni-stuttgart.de","User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0","Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language: en-US,en;q=0.5","Accept-Encoding: ",#  gzip, deflate Don't want to uncompress it later
		"DNT: 1","Referer: https://ilias3.uni-stuttgart.de/login.php?client_id=Uni_Stuttgart&lang=de","Connection: keep-alive"])
	try:
		c.perform()
		if os.path.exists(cookie):
			print "[+]    Cookie succssfully set"
		c.close()
		return cookie

	except pycurl.error, error:
		errno, errstr = error
		print '[-]    An error occurred trying to login in Ilias: ', errstr
		return cookie
	finally:
		c.close()


def get(config, section, option, default=None):
	try:
		return config.get(section, option)
	except:
		return default

def download(curl,cmd,url,stats):
	#Read res
	print ""
	print "[+]    Reading ",str(url),
	try:
		buf = cStringIO.StringIO()
		curl.setopt(pycurl.URL, url)
		curl.setopt(pycurl.WRITEFUNCTION, buf.write)
		curl.perform()
		html = buf.getvalue()
		buf.close()
		#curl.unsetopt(pycurl.WRITEFUNCTION) bug??
		#curl.reset()
		curl.setopt(pycurl.VERBOSE, 0)
		curl.setopt(pycurl.FOLLOWLOCATION, 1);
		#setup authentification
		curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_ANY);
		curl.setopt(pycurl.USERPWD, cmd.login+":"+cmd.pssw);
		#curl.setopt(pycurl.NOPROGRESS, 0)

		print "[+]    OK"
		stats[0] += 1 

		#cmd.regex = str(cmd.regex)
		print "[+]    '" + str(cmd.regex)
		p = re.compile(''.join(cmd.regex))
		matches = p.findall(html)
		if len(matches) == 0:
			print "[-]    Nothing found"


		if not os.path.isdir("./" + cmd.outDir):
			os.makedirs("./" + cmd.outDir)

		for match in matches:
			print "[+]    '" + match + "' ...",
			file_name = cmd.outDir + match.split('/')[-1]
			if not os.path.exists(file_name):
				f = None
				try:
					f = open(file_name, 'wb')
					curl.setopt(pycurl.URL, urljoin(cmd.url, match))
					curl.setopt(pycurl.FILE, f);
					curl.perform()
					print "[+]    OK"
					stats[2] += 1

				except pycurl.error, error:
					errno, errstr = error
					print "[-]    Failed", errstr
					stats[4]+=1
				finally:
					if not f is None:
						f.close()
			else:
				print "[-]    skipped"
				stats[3] += 1
	except pycurl.error, error:
		errno, errstr = error
		print "[-]    Failed", errstr
		stats[1] +=1



#Read ./config.ini
print "[+]    Reading ./config.ini ...",
config = ConfigParser.ConfigParser()

config.read("./config.ini");
print "[+]    OK"

commands = []
#Parse ./config.ini
print "[+]    Parsing ./config.ini :"
for section in config.sections():
	print "[+]    Found section '"+section+"'"
	cmd = Command()
	cmd.url           = get(config, section, "url") # TODO Should remove last slash from URL!!
	cmd.outDir        = get(config, section, "outDir", "./")
	if get(config, section, "askAuth") != "true":
		cmd.login         = get(config, section, "login",  "")
		cmd.pssw          = get(config, section, "pssw",   "")
	else:
		print "  login: ",
		cmd.login = raw_input()
		print "  pssw:  ",
		cmd.pssw  = raw_input()

	if (get(config, section, "ilias") != "false"):
		cmd.ilias        = get(config, section, "ilias",   "")
		# regexarray for ilias
		cmd.regex = [e.strip() for e in get(config,section,"regex").split(',')]

	else:
		cmd.regex         = get(config, section, "regex")
	print "[+]    Regex is:", cmd.regex
	commands.append(cmd)
print "[+]    Done"

stats = [0,0,0,0,0] #Geht deutlich sch
#resRead   = 0
#resFailed = 0
#downloaded = 0 
#skipped    = 0
#failed     = 0

#read commands
curl = pycurl.Curl()
downurl = []
for cmd in commands:
	curl.reset()
	curl.setopt(pycurl.VERBOSE, 0)
	curl.setopt(pycurl.FOLLOWLOCATION, 1);
	#setup authentification
	curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_ANY);
	curl.setopt(pycurl.USERPWD, cmd.login+":"+cmd.pssw);
	## Ilias functions...
	if cmd.ilias:
		cookie = loginilias(cmd)
		curl.setopt(pycurl.COOKIEFILE,cookie )
		downurl = findLinks(cmd.url,cmd.regex, curl)
		cmd.regex = cmd.regex[len(cmd.regex)-1] #den letzten setzten...
		print cmd.regex
		for url in downurl:
			download(curl,cmd,url,stats)
			del downurl[:]
		logoutilias(curl)
	
	else: # usual case
		download(curl,cmd,cmd.url,stats)
curl.close()

print "";
print "Resources:";
print "  read:   %d" % (stats[0],);
print "  failed: %d" % (stats[1],);
print "Files:"
print "  downloaded: %d" % (stats[2],);
print "  skipped:    %d" % (stats[3],);
print "  failed:     %d" % (stats[4],);
if stats[1] + stats[4] == 0:
	print "[+]    Success";
else:
	print "[-]    Errors occured";

############################################
#def getiliaslinks(curl,cookie,cmd,num):
#	if 'download&client' in cmd.url:
#		return cmd.url
#	if len(cmd.regex) == num:
#		return cmd.url
#	else:
#		print cmd.regex[num]
#		for url in cmd.url:
#			if len(url) <=2:
#				url=cmd.url
#			print "URL: ",url
#			buf = cStringIO.StringIO()
#			curl.setopt(pycurl.COOKIEFILE,cookie)
#			curl.setopt(pycurl.URL, url)
#			curl.setopt(pycurl.WRITEFUNCTION, buf.write)
#			curl.perform()
#			html = buf.getvalue()
#			 curl.reset() (want to keep cookie)
#			curl.setopt(pycurl.VERBOSE, 0)
#			curl.setopt(pycurl.FOLLOWLOCATION, 1);
#			buf.close()
#			print "searching for regex '" + cmd.regex[num] + "' :"
#			p = re.compile(cmd.regex[num])
#			linkmatches = p.findall(html)
#			num=num+1
#			q = re.compile(cmd.regex[num])
#			for links in linkmatches:
#				matches = q.findall(links)
#				if len(matches) == 0:
#					print "Nothing found"
#					getiliaslinks(curl,cookie,cmd,num+1)
#				else:
#					for i in matches:
#						print i
#					cmd.links = matches
#					getiliaslinks(curl,cookie,cmd,num+1)



