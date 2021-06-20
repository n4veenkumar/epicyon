__filename__ = "session.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "1.2.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"
__module_group__ = "Core"

import os
import requests
from utils import urlPermitted
import json
from socket import error as SocketError
import errno
from http.client import HTTPConnection

baseDirectory = None


def createSession(proxyType: str):
    session = None
    try:
        session = requests.session()
    except requests.exceptions.RequestException as e:
        print('WARN: requests error during createSession ' + str(e))
        return None
    except SocketError as e:
        if e.errno == errno.ECONNRESET:
            print('WARN: connection was reset during createSession ' + str(e))
        else:
            print('WARN: socket error during createSession ' + str(e))
        return None
    except ValueError as e:
        print('WARN: error during createSession ' + str(e))
        return None
    if not session:
        return None
    if proxyType == 'tor':
        session.proxies = {}
        session.proxies['http'] = 'socks5h://localhost:9050'
        session.proxies['https'] = 'socks5h://localhost:9050'
    elif proxyType == 'i2p':
        session.proxies = {}
        session.proxies['http'] = 'socks5h://localhost:4447'
        session.proxies['https'] = 'socks5h://localhost:4447'
    elif proxyType == 'gnunet':
        session.proxies = {}
        session.proxies['http'] = 'socks5h://localhost:7777'
        session.proxies['https'] = 'socks5h://localhost:7777'
    # print('New session created with proxy ' + str(proxyType))
    return session


def urlExists(session, url: str, timeoutSec=3,
              httpPrefix='https', domain='testdomain') -> bool:
    if not isinstance(url, str):
        print('url: ' + str(url))
        print('ERROR: urlExists failed, url should be a string')
        return False
    sessionParams = {}
    sessionHeaders = {}
    sessionHeaders['User-Agent'] = 'Epicyon/' + __version__
    if domain:
        sessionHeaders['User-Agent'] += \
            '; +' + httpPrefix + '://' + domain + '/'
    if not session:
        print('WARN: urlExists failed, no session specified')
        return True
    try:
        result = session.get(url, headers=sessionHeaders,
                             params=sessionParams,
                             timeout=timeoutSec)
        if result:
            if result.status_code == 200 or \
               result.status_code == 304:
                return True
            else:
                print('urlExists for ' + url + ' returned ' +
                      str(result.status_code))
    except BaseException:
        pass
    return False


def getJson(session, url: str, headers: {}, params: {}, debug: bool,
            version: str = '1.2.0', httpPrefix: str = 'https',
            domain: str = 'testdomain',
            timeoutSec: int = 20, quiet: bool = False) -> {}:
    if not isinstance(url, str):
        if debug and not quiet:
            print('url: ' + str(url))
            print('ERROR: getJson failed, url should be a string')
        return None
    sessionParams = {}
    sessionHeaders = {}
    if headers:
        sessionHeaders = headers
    if params:
        sessionParams = params
    sessionHeaders['User-Agent'] = 'Epicyon/' + version
    if domain:
        sessionHeaders['User-Agent'] += \
            '; +' + httpPrefix + '://' + domain + '/'
    if not session:
        if not quiet:
            print('WARN: getJson failed, no session specified for getJson')
        return None

    if debug:
        HTTPConnection.debuglevel = 1

    try:
        result = session.get(url, headers=sessionHeaders,
                             params=sessionParams, timeout=timeoutSec)
        if result.status_code != 200:
            if result.status_code == 401:
                print('WARN: getJson Unauthorized url: ' + url)
            elif result.status_code == 403:
                print('WARN: getJson Forbidden url: ' + url)
            elif result.status_code == 404:
                print('WARN: getJson Not Found url: ' + url)
            else:
                print('WARN: getJson url: ' + url +
                      ' failed with error code ' +
                      str(result.status_code))
        return result.json()
    except requests.exceptions.RequestException as e:
        sessionHeaders2 = sessionHeaders.copy()
        if sessionHeaders2.get('Authorization'):
            sessionHeaders2['Authorization'] = 'REDACTED'
        if debug and not quiet:
            print('ERROR: getJson failed, url: ' + str(url) + ', ' +
                  'headers: ' + str(sessionHeaders2) + ', ' +
                  'params: ' + str(sessionParams) + ', ' + str(e))
    except ValueError as e:
        sessionHeaders2 = sessionHeaders.copy()
        if sessionHeaders2.get('Authorization'):
            sessionHeaders2['Authorization'] = 'REDACTED'
        if debug and not quiet:
            print('ERROR: getJson failed, url: ' + str(url) + ', ' +
                  'headers: ' + str(sessionHeaders2) + ', ' +
                  'params: ' + str(sessionParams) + ', ' + str(e))
    except SocketError as e:
        if not quiet:
            if e.errno == errno.ECONNRESET:
                print('WARN: getJson failed, ' +
                      'connection was reset during getJson ' + str(e))
    return None


def postJson(session, postJsonObject: {}, federationList: [],
             inboxUrl: str, headers: {}, timeoutSec: int = 60,
             quiet: bool = False) -> str:
    """Post a json message to the inbox of another person
    """
    # check that we are posting to a permitted domain
    if not urlPermitted(inboxUrl, federationList):
        if not quiet:
            print('postJson: ' + inboxUrl + ' not permitted')
        return None

    try:
        postResult = \
            session.post(url=inboxUrl,
                         data=json.dumps(postJsonObject),
                         headers=headers, timeout=timeoutSec)
    except requests.Timeout as e:
        if not quiet:
            print('ERROR: postJson timeout ' + inboxUrl + ' ' +
                  json.dumps(postJsonObject) + ' ' + str(headers))
            print(e)
        return ''
    except requests.exceptions.RequestException as e:
        if not quiet:
            print('ERROR: postJson requests failed ' + inboxUrl + ' ' +
                  json.dumps(postJsonObject) + ' ' + str(headers) +
                  ' ' + str(e))
        return None
    except SocketError as e:
        if not quiet and e.errno == errno.ECONNRESET:
            print('WARN: connection was reset during postJson')
        return None
    except ValueError as e:
        if not quiet:
            print('ERROR: postJson failed ' + inboxUrl + ' ' +
                  json.dumps(postJsonObject) + ' ' + str(headers) +
                  ' ' + str(e))
        return None
    if postResult:
        return postResult.text
    return None


def postJsonString(session, postJsonStr: str,
                   federationList: [],
                   inboxUrl: str,
                   headers: {},
                   debug: bool,
                   timeoutSec: int = 30,
                   quiet: bool = False) -> (bool, bool):
    """Post a json message string to the inbox of another person
    The second boolean returned is true if the send is unauthorized
    NOTE: Here we post a string rather than the original json so that
    conversions between string and json format don't invalidate
    the message body digest of http signatures
    """
    try:
        postResult = \
            session.post(url=inboxUrl, data=postJsonStr,
                         headers=headers, timeout=timeoutSec)
    except requests.exceptions.RequestException as e:
        if not quiet:
            print('WARN: error during postJsonString requests ' + str(e))
        return None, None
    except SocketError as e:
        if not quiet and e.errno == errno.ECONNRESET:
            print('WARN: connection was reset during postJsonString')
        if not quiet:
            print('ERROR: postJsonString failed ' + inboxUrl + ' ' +
                  postJsonStr + ' ' + str(headers))
        return None, None
    except ValueError as e:
        if not quiet:
            print('WARN: error during postJsonString ' + str(e))
        return None, None
    if postResult.status_code < 200 or postResult.status_code > 202:
        if postResult.status_code >= 400 and \
           postResult.status_code <= 405 and \
           postResult.status_code != 404:
            if not quiet:
                print('WARN: Post to ' + inboxUrl +
                      ' is unauthorized. Code ' +
                      str(postResult.status_code))
            return False, True
        else:
            if not quiet:
                print('WARN: Failed to post to ' + inboxUrl +
                      ' with headers ' + str(headers))
                print('status code ' + str(postResult.status_code))
            return False, False
    return True, False


def postImage(session, attachImageFilename: str, federationList: [],
              inboxUrl: str, headers: {}) -> str:
    """Post an image to the inbox of another person or outbox via c2s
    """
    # check that we are posting to a permitted domain
    if not urlPermitted(inboxUrl, federationList):
        print('postJson: ' + inboxUrl + ' not permitted')
        return None

    if not (attachImageFilename.endswith('.jpg') or
            attachImageFilename.endswith('.jpeg') or
            attachImageFilename.endswith('.png') or
            attachImageFilename.endswith('.svg') or
            attachImageFilename.endswith('.gif')):
        print('Image must be png, jpg, gif or svg')
        return None
    if not os.path.isfile(attachImageFilename):
        print('Image not found: ' + attachImageFilename)
        return None
    contentType = 'image/jpeg'
    if attachImageFilename.endswith('.png'):
        contentType = 'image/png'
    if attachImageFilename.endswith('.gif'):
        contentType = 'image/gif'
    if attachImageFilename.endswith('.svg'):
        contentType = 'image/svg+xml'
    headers['Content-type'] = contentType

    with open(attachImageFilename, 'rb') as avFile:
        mediaBinary = avFile.read()
        try:
            postResult = session.post(url=inboxUrl, data=mediaBinary,
                                      headers=headers)
        except requests.exceptions.RequestException as e:
            print('WARN: error during postImage requests ' + str(e))
            return None
        except SocketError as e:
            if e.errno == errno.ECONNRESET:
                print('WARN: connection was reset during postImage')
            print('ERROR: postImage failed ' + inboxUrl + ' ' +
                  str(headers) + ' ' + str(e))
            return None
        except ValueError as e:
            print('WARN: error during postImage ' + str(e))
            return None
        if postResult:
            return postResult.text
    return None
