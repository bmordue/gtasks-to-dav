# cf http://www.whitemiceconsulting.com/2010/04/performing-propfind-from-python.html
import httplib
import hashlib

# Caldav url
url = "http://dav.benmordue.co.uk/cal.php/calendars/labuser/"
calendar_url = "http://dav.benmordue.co.uk/cal.php/calendars/labuser/named"

USERNAME = "labuser"
PASSWORD="tester"
SERVER_HOST = 'dav.benmordue.co.uk'
SERVER_PORT = 80
SERVER_PATH = '/cal.php/calendars/labuser/'
CLIENT_AGENT = 'example_httplib/v1'

CAL_EVENT = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:1234567890
DTSTAMP:20150109T095500Z
DTSTART:20150109T170000Z
DTEND:20150109T180000Z
SUMMARY:This is an event from caldav-python
END:VEVENT
END:VCALENDAR
"""

CAL_TODO = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VTODO
UID:1234567891
DTSTAMP:20150109T095500Z
DTSTART:20150109T170000Z
DUE:20150109T180000Z
SUMMARY:TODO from caldav-python
END:VTODO
END:VCALENDAR
"""

FIND_ALL = """<?xml version="1.0" encoding="utf-8"?>
<propfind xmlns="DAV:">
<prop>
<getetag/>
</prop>
</propfind>"""

PRIN="""<d:propfind xmlns:d="DAV:">
  <d:prop>
     <d:current-user-principal />
  </d:prop>
</d:propfind>"""

CALHOME="""<d:propfind xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
  <d:prop>
     <c:calendar-home-set />
  </d:prop>
</d:propfind>"""

DEPTH="""<d:propfind xmlns:d="DAV:" xmlns:cs="http://calendarserver.org/ns/" xmlns:c="urn:ietf:params:xml:ns:caldav">
  <d:prop>
     <d:resourcetype />
     <d:displayname />
     <cs:getctag />
     <c:supported-calendar-component-set />
  </d:prop>
</d:propfind>"""


#header = 'Digest realm="BaikalDAV",qop="auth",nonce="54afb3a050fd7",opaque="df58bdff8cf60599c939187d0b5c54de"'
def parse_auth_header(header):
    values = {}
    details = header.split()[1] #ignore first item in list, "Digest"
    tokens = details.split(',') 
    for t in tokens:
        k,v = t.split('=')
        values[k] = v.strip('"')
    return values

def digest_response(authheader, method, uri):
    headerdict = parse_auth_header(authheader)
    realm = headerdict['realm']
    nonce = headerdict['nonce']
    qop = headerdict['qop']
    noncecount = "00000001"
    CLIENT_NONCE = "777777"
    m1 = hashlib.md5(':'.join([USERNAME,realm,PASSWORD]))
    m2 = hashlib.md5(':'.join([method,uri]))
    ha1 = m1.hexdigest()
    ha2 = m2.hexdigest()
    m3 = hashlib.md5(':'.join([ha1,nonce,noncecount,CLIENT_NONCE,qop,ha2]))
    response = m3.hexdigest()
    print response
    authdetails = []
    authdetails.append('username="'+USERNAME+'"')
    authdetails.append('realm="'+realm+'"')
    authdetails.append('nonce="'+nonce+'"')
    authdetails.append('uri="'+uri+'"')
    authdetails.append('qop='+qop)
    authdetails.append('nc="'+noncecount+'"')
    authdetails.append('cnonce="'+CLIENT_NONCE+'"')
    authdetails.append('response="'+response+'"')
    authdetails.append('opaque="'+headerdict['opaque']+'"')
        
    dh = "Digest " + ",".join(authdetails)
    print "Authorization (digest_response): %s" % dh
    return dh

def make_request(method, server_path, content):
    connection = httplib.HTTPConnection(SERVER_HOST, SERVER_PORT)
    connection.putrequest(method, server_path)
    auth_string = ''
    connection.putheader('Authorization', auth_string)
    connection.putheader('User-Agent', CLIENT_AGENT)
    connection.putheader('Depth', 1)
    connection.putheader('Content-Length', str(len(content)))
    connection.endheaders()
    connection.send(content)
    response = connection.getresponse()
    
    print "Response status: %s" % response.status
    print "Response headers: "
    for header, value in response.getheaders():
        print "%s : %s" % (header, value)
    
    if response.status == 401:
        authheader = response.getheader("www-authenticate")
        digestheader = digest_response(authheader, method, server_path)
        
        connection.close()
        response = None
        connection = httplib.HTTPConnection(SERVER_HOST, SERVER_PORT)
        connection.putrequest(method, server_path)
        connection.putheader('Authorization', digestheader)
        connection.putheader('User-Agent', CLIENT_AGENT)
        connection.putheader('Depth', 1)
        connection.putheader('Content-Length', str(len(content)))
#        connection.putheader('If-None-Match', '*')

        connection.endheaders()
        connection.send(content)
        response = connection.getresponse()
        print ''
        print ''
        print "Response status: %s" % response.status
        print "Response headers: "
        for header, value in response.getheaders():
            print "%s : %s" % (header, value)
        print response.read()

def main():
    make_request("PROPFIND", "http://dav.benmordue.co.uk/cal.php/calendars/labuser/named/", DEPTH)
    # make_request("PUT", "/cal.php/calendars/labuser/named/todo2.ics", CAL_TODO)
    f = open('../tusks/out.ics', 'r');
    # make_request("PUT", "/cal.php/calendars/labuser/named/gtasks.ics", f.read());
    f.close();

if __name__ == "__main__":
    main()