__filename__ = "utils.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "0.0.1"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

import os
import datetime
from capabilities import isCapable

def getStatusNumber() -> (str,str):
    """Returns the status number and published date
    """
    currTime=datetime.datetime.utcnow()
    daysSinceEpoch=(currTime - datetime.datetime(1970,1,1)).days
    # status is the number of seconds since epoch
    statusNumber=str(((daysSinceEpoch*24*60*60) + (currTime.hour*60*60) + (currTime.minute*60) + currTime.second)*1000000 + currTime.microsecond)
    published=currTime.strftime("%Y-%m-%dT%H:%M:%SZ")
    conversationDate=currTime.strftime("%Y-%m-%d")
    return statusNumber,published

def createPersonDir(nickname: str,domain: str,baseDir: str,dirname: str) -> str:
    """Create a directory for a person
    """
    handle=nickname.lower()+'@'+domain.lower()
    if not os.path.isdir(baseDir+'/accounts/'+handle):
        os.mkdir(baseDir+'/accounts/'+handle)
    boxDir=baseDir+'/accounts/'+handle+'/'+dirname
    if not os.path.isdir(boxDir):
        os.mkdir(boxDir)
    return boxDir

def createOutboxDir(nickname: str,domain: str,baseDir: str) -> str:
    """Create an outbox for a person
    """
    return createPersonDir(nickname,domain,baseDir,'outbox')

def createInboxQueueDir(nickname: str,domain: str,baseDir: str) -> str:
    """Create an inbox queue and returns the feed filename and directory
    """
    return createPersonDir(nickname,domain,baseDir,'queue')

def domainPermitted(domain: str, federationList: []):
    if len(federationList)==0:
        return True
    if domain in federationList:
        return True
    return False

def urlPermitted(url: str, federationList: [],capsList: [],capability: str):
    if capsList:
        if not isCapable(url,capsList,capability):
            return False            
    if len(federationList)==0:
        return True
    for domain in federationList:
        if domain in url:
            return True
    return False

def getNicknameFromActor(actor: str) -> str:
    """Returns the nickname from an actor url
    """
    if '/users/' not in actor:
        return None
    return actor.split('/users/')[1].replace('@','')    

def getDomainFromActor(actor: str) -> (str,int):
    """Returns the domain name from an actor url
    """
    port=None
    if '/users/' not in actor:
        domain = actor.replace('https://','').replace('http://','').replace('dat://','')
    else:
        domain = actor.split('/users/')[0].replace('https://','').replace('http://','').replace('dat://','')
    if ':' in domain:
        port=int(domain.split(':')[1])
        domain=domain.split(':')[0]
    return domain,port
    
def followPerson(baseDir: str,nickname: str, domain: str, \
                 followNickname: str, followDomain: str, \
                 federationList: [],debug: bool, \
                 followFile='following.txt') -> bool:
    """Adds a person to the follow list
    """
    if not domainPermitted(followDomain.lower().replace('\n',''), \
                           federationList):
        if debug:
            print('DEBUG: follow of domain '+followDomain+' not permitted')
        return False
    handle=nickname.lower()+'@'+domain.lower()
    handleToFollow=followNickname.lower()+'@'+followDomain.lower()
    if not os.path.isdir(baseDir+'/accounts'):
        os.mkdir(baseDir+'/accounts')
    if not os.path.isdir(baseDir+'/accounts/'+handle):
        os.mkdir(baseDir+'/accounts/'+handle)
    filename=baseDir+'/accounts/'+handle+'/'+followFile
    if os.path.isfile(filename):
        if handleToFollow in open(filename).read():
            return True
        with open(filename, "a") as followfile:
            followfile.write(handleToFollow+'\n')
            return True
    with open(filename, "w") as followfile:
        followfile.write(handleToFollow+'\n')
    return True
