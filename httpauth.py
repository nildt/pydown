#!/usr/bin/python

from bs4 import BeautifulSoup
import urllib2 
import base64
import re
import io


class WebsiteModul(object):
	def __init__(self,url,username,password,regex):
		try:
			self.url = url
			self.username = username
			self.password = password
			self.regex = regex
			# MakeRequest
			request = urllib2.Request(url)
			# Authentication
			auth64 = base64.encodestring('%s:%s' % (username,password)).replace('\n', '')
			request.add_header("Authorization", "Basic %s" % auth64)
			# realRequest
			content = urllib2.urlopen(request)
			# CreateRegex
			soup = BeautifulSoup(content)
			# parse and find pdfs
			a = ""
			for tag in soup.findAll('a', attrs={'href': re.compile(regex)}):
				#print tag['href']
				self.download(tag['href'],password,username)

		except urllib2.URLError as err: pass  # Later: log_err or sth like that, look at log class...


	def download(self,url,password,username):
		# concat url
		url = "http://www.pi2.uni-stuttgart.de/cms/" + url
		# Get Filename
		file_name = url.split('/')[-1]
		# MakeRequest
		request = urllib2.Request(url)
		# Authentication
		auth64 = base64.encodestring('%s:%s' % (username,password)).replace('\n', '')
		request.add_header("Authorization", "Basic %s" % auth64)
		# realRequest
		u = urllib2.urlopen(request)
		# FileHandling
		f = open(file_name, 'wb')
		# FileMetaData
		meta = u.info()
		file_size = int(meta.getheaders("Content-Length")[0])
		print "Downloading: %s Bytes: %s" % (file_name, file_size)
		# Downlaod from https://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
		file_size_dl = 0
		block_sz = 8192
		while True:
			buffer = u.read(block_sz)
			if not buffer:
				break
			file_size_dl += len(buffer)
			f.write(buffer)
			status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
			status = status + chr(8)*(len(status)+1)
			print status
		f.close()

# Watch out, password and username are hidden...
test = WebsiteModul("http://www.pi2.uni-stuttgart.de/cms/index.php?article_id=207","username", "password", "[A-Z]\w+[.]+[pdf]")
