#!/usr/bin/python
#coding: utf

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
        ilias = ""

def get(config, section, option, default=None):
        try:
                return config.get(section, option)
        except:
                return default

#def getFileName(url):
#       headers = cStringIO.StringIO()
#       c = pycurl.Curl()
#       c.setopt(c.URL, url)
#       c.setopt(c.HEADER, 1)
#       c.setopt(c.WRITEFUNCTION, lambda x: None)
#       c.setopt(c.VERBOSE,0)
#       c.setopt(c.NOBODY, 1) # header only, no body
#       c.setopt(c.HEADERFUNCTION, headers.write)
#       c.setopt(c.COOKIEFILE,"iliascookie.txt")
#       c.perform()
#       header = headers.getvalue()
#       print "#########HEADER"
#       print re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", header)
#       print "#########HEADERENDE"
#       c.close()
#

def download(curl,cmd,url):
        print "[+]    Reading ",str(url),
        try:
                if not os.path.isdir("./" + cmd.outDir):
                        os.makedirs("./" + cmd.outDir)
                print "[+]    '" + url + "' ...",
                #getFileName(url)
                file_name = cmd.outDir +url.split('/')[-1]
                if not os.path.exists(file_name):
                        f = None
                        try:
                                f = open(file_name, 'wb')
                                curl.setopt(pycurl.URL, url)
                                curl.setopt(pycurl.FILE, f);
                                curl.perform()
                        except pycurl.error, error:
                                errstr = error
                                print "[-]    Failed", errstr
                        finally:
                                if not f is None:
                                        f.close()
                else:
                        print "[+]    File already exists: ", file_name
        except pycurl.error, error:
                errno, errstr = error
                print "[-]    Failed", errstr

def logoutilias(curl,cookie):
        curl.setopt(pycurl.URL, "https://ilias3.uni-stuttgart.de/logout.php?lang=de")
        curl.setopt(pycurl.VERBOSE, 0)
        curl.setopt(pycurl.FOLLOWLOCATION, 0)
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
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEFUNCTION, buf.write)
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
        curl.perform()
        html = buf.getvalue()
        #print html
#       with open ('debug.html', 'a') as f: f.write (html)
        buf.close()
        return html

def findLinks(url,regex,curl,links):
        try:
                html = loadHtml(curl, url)
                print "DEBUG"
                print "Aktueller Regex[0] ist: ",regex[0]
                print "URL ist: ",url
                print "len(html) ist: ",len(html)
                print "len(regex) ist: ",len(regex)
                print "links ist: ",links
                p = re.compile(regex[0],re.IGNORECASE)
                matches = p.findall(html)
                if len(regex) == 1:
                        for match in matches:
                                site = urljoin(url,match)
                                links.add(site)
                else:
                        for match in matches:
                                site = urljoin(url, match)
                                findLinks(site,regex[1:],curl,links)
                return links
        except Exception,e:
                print "Exception in findLinks..."
                print e

def loginilias(cmd):
        cookie = 'iliascookie.txt'
        if  os.stat(cookie).st_size==0: # Cookie noch leer / nicht existent...TODO Was passiert wenn kein iliascookie.txt?
                print "[+]    Entered ilias"
                c = pycurl.Curl()
                data = "password=" + cmd.pssw + "&" + "username=" + cmd.login
                c.setopt(c.URL, "https://ilias3.uni-stuttgart.de/login.php?target=&soap_pw=&ext_uid=&cookies=nocookies&client_id=Uni_Stuttgart&lang=de")
                c.setopt(c.POST,1)
                c.setopt(c.POSTFIELDS, data)
                c.setopt(c.FOLLOWLOCATION, 1)
                c.setopt(c.WRITEFUNCTION, lambda x: None)
                c.COOKIESESSION = 96
                c.setopt(c.COOKIESESSION, True);
                c.setopt(c.COOKIEJAR, cookie)
                c.setopt(c.FAILONERROR, False)
                c.setopt(c.VERBOSE,0)
                c.setopt(c.HTTPHEADER, ["Host: ilias3.uni-stuttgart.de","User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0","Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language: en-US,en;q=0.5","Accept-Encoding: ",#  gzip, deflate Don't want to uncompress it later
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
        else:
                print "[+]    Cookie was already set!"
                return cookie
def newCurl():
        curl = pycurl.Curl()
        curl.setopt(pycurl.VERBOSE, 0)
        curl.setopt(pycurl.FOLLOWLOCATION, 1);
        curl.setopt(pycurl.NOPROGRESS,1)
        curl.setopt(pycurl.HEADER, False)
        curl.setopt(pycurl.MAXREDIRS, 10)
        return curl

def main():
    try:
        print "[+]    Reading ./config.ini ...",
        config = ConfigParser.ConfigParser()
        if os.path.isfile('config.ini'):
                config.read("./config.ini");
        else:
                raise Exception("[-]    There is no /config.ini!")
        commands = []
        print "[+]    Parsing ./config.ini :"

        for section in config.sections():
                print "[+]    Found section: ",section
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
                        cmd.regex = [e.strip() for e in get(config,section,"regex").split(',')]
                else:
                        cmd.regex         = get(config, section, "regex")
                        # Trailing slash entfernen...
                        cmd.url.rstrip('\\')
                commands.append(cmd)
        print "[+]    Successfull parsed config.ini!"


        for cmd in commands:
                links = set()
                if cmd.ilias:
                        curl = newCurl()
                        cookie = loginilias(cmd)
                        curl.setopt(pycurl.COOKIEFILE,cookie )
                        links = findLinks(cmd.url,cmd.regex,curl,links)

                        for url in list(links):
                                download(curl,cmd,url)
                                logoutilias(curl,cookie)
                                curl.close()
                else:
                        curl = newCurl()
                        curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_ANY);
                        curl.setopt(pycurl.USERPWD, cmd.login+":"+cmd.pssw);
                        links = findLinks(cmd.url,cmd.regex,curl,links)
                        for url in list(links):
                                download(curl,cmd,url)
                                curl.close()
        print "[+]    Success";

    except KeyboardInterrupt:
                if os.path.exists(cookie):
                        open(cookie, 'w').close()
                        print "[+]    Cookie deleted!"
                else:
                        print "[-]    Couldn't delete Cookie"
                curl.close()
                print "[-]    Shutdown requested...exiting"
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(0)

if __name__ == "__main__":
    main()
