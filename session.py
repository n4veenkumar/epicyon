__filename__ = "session.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "0.0.1"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

import requests
from requests_toolbelt.adapters.source import SourceAddressAdapter
from utils import urlPermitted
import json

baseDirectory=None

def createSession(domain: str, port: int, onionRoute: bool):
    session = requests.session()
    #if domain.startswith('127.') or domain.startswith('192.') or domain.startswith('10.'):
    #    session.mount('http://', SourceAddressAdapter(domain))
        #session.mount('http://', SourceAddressAdapter((domain, port)))
    if onionRoute:
        session.proxies = {}
        session.proxies['http'] = 'socks5h://localhost:9050'
        session.proxies['https'] = 'socks5h://localhost:9050'
    return session

def getJson(session,url: str,headers: {},params: {}) -> {}:
    sessionParams={}
    sessionHeaders={}
    if headers:
        sessionHeaders=headers
    if params:
        sessionParams=params
    sessionHeaders['User-agent'] = "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 5 Build/LMY48B; wv)"
    session.cookies.clear()
    result=session.get(url, headers=sessionHeaders, params=sessionParams)
    #print("*****result "+url+' ' + str(result))
    return result.json()

def postJson(session,postJsonObject: {},federationList: [],inboxUrl: str,headers: {}) -> str:
    """Post a json message to the inbox of another person
    """
    # check that we are posting to a permitted domain
    if not urlPermitted(inboxUrl,federationList):
        return None

    postResult = session.post(url = inboxUrl, data = json.dumps(postJsonObject), headers=headers)
    return postResult.text
