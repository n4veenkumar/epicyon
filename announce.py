__filename__ = "announce.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "0.0.1"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

import json
import commentjson
from utils import getStatusNumber
from utils import createOutboxDir
from utils import urlPermitted

def createAnnounce(baseDir: str,federationList: [], \
                   nickname: str, domain: str, port: int, \
                   toUrl: str, ccUrl: str, httpPrefix: str, \
                   objectUrl: str, saveToFile: bool) -> {}:
    """Creates an announce message
    Typically toUrl will be https://www.w3.org/ns/activitystreams#Public
    and ccUrl might be a specific person favorited or repeated and the
    followers url objectUrl is typically the url of the message,
    corresponding to url or atomUri in createPostBase
    """
    if not urlPermitted(objectUrl,federationList,"inbox:write"):
        return None

    if port!=80 and port!=443:
        domain=domain+':'+str(port)

    statusNumber,published = getStatusNumber()
    newAnnounceId= \
        httpPrefix+'://'+domain+'/users/'+nickname+'/statuses/'+statusNumber
    newAnnounce = {
        'actor': httpPrefix+'://'+domain+'/users/'+nickname,
        'atomUri': httpPrefix+'://'+domain+'/users/'+nickname+'/statuses/'+statusNumber,
        'cc': [],
        'id': newAnnounceId+'/activity',
        'object': objectUrl,
        'published': published,
        'to': [toUrl],
        'type': 'Announce'
    }
    if ccUrl:
        if len(ccUrl)>0:
            newAnnounce['cc']=ccUrl
    if saveToFile:
        if ':' in domain:
            domain=domain.split(':')[0]
        outboxDir = createOutboxDir(nickname,domain,baseDir)
        filename=outboxDir+'/'+newAnnounceId.replace('/','#')+'.json'
        with open(filename, 'w') as fp:
            commentjson.dump(newAnnounce, fp, indent=4, sort_keys=False)
    return newAnnounce

def announcePublic(baseDir: str,federationList: [], \
                   nickname: str, domain: str, port: int, httpPrefix: str, \
                   objectUrl: str, saveToFile: bool) -> {}:
    """Makes a public announcement
    """
    fromDomain=domain
    if port!=80 and port!=443:
        fromDomain=fromDomain+':'+str(port)

    toUrl = 'https://www.w3.org/ns/activitystreams#Public'
    ccUrl = httpPrefix + '://'+fromDomain+'/users/'+nickname+'/followers'
    return createAnnounce(baseDir,nickname, domain, port, \
                          toUrl, ccUrl, httpPrefix, objectUrl, saveToFile)

def repeatPost(baseDir: str,federationList: [], \
               nickname: str, domain: str, port: int, httpPrefix: str, \
               announceNickname: str, announceDomain: str, \
               announcePort: int, announceHttpsPrefix: str, \
               announceStatusNumber: int, saveToFile: bool) -> {}:
    """Repeats a given status post
    """
    announcedDomain=announceDomain
    if announcePort!=80 and announcePort!=443:
        announcedDomain=announcedDomain+':'+str(announcePort)

    objectUrl = announceHttpsPrefix + '://'+announcedDomain+'/users/'+ \
        announceNickname+'/statuses/'+str(announceStatusNumber)

    return announcePublic(baseDir,nickname, domain, port, \
                          httpPrefix, objectUrl, saveToFile)

