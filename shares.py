__filename__ = "shares.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "0.0.1"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

import json
import commentjson
import os
import time
from shutil import copyfile
from webfinger import webfingerHandle
from auth import createBasicAuthHeader
from posts import getPersonBox
from session import postJson
from utils import validNickname
from utils import getNicknameFromActor
from utils import getDomainFromActor
from media import removeMetaData

def removeShare(baseDir: str,nickname: str,domain: str, \
                displayName: str) -> None:
    """Removes a share for a person
    """
    sharesFilename=baseDir+'/accounts/'+nickname+'@'+domain+'/shares.json'
    if os.path.isfile(sharesFilename):    
        with open(sharesFilename, 'r') as fp:
            sharesJson=commentjson.load(fp)

    itemID=displayName.replace(' ','')
    if sharesJson.get(itemID):
        # remove any image for the item
        itemIDfile=baseDir+'/sharefiles/'+itemID
        if sharesJson[itemID]['imageUrl']:
            if sharesJson[itemID]['imageUrl'].endswith('.png'):
                os.remove(itemIDfile+'.png')
            if sharesJson[itemID]['imageUrl'].endswith('.jpg'):
                os.remove(itemIDfile+'.jpg')
            if sharesJson[itemID]['imageUrl'].endswith('.gif'):
                os.remove(itemIDfile+'.gif')
        # remove the item itself
        del sharesJson[itemID]
        with open(sharesFilename, 'w') as fp:
            commentjson.dump(sharesJson, fp, indent=4, sort_keys=True)

def addShare(baseDir: str, \
             httpPrefix: str,nickname: str,domain: str,port: int, \
             displayName: str, \
             summary: str, \
             imageFilename: str, \
             itemType: str, \
             itemCategory: str, \
             location: str, \
             duration: str,
             debug: bool) -> None:
    """Updates the likes collection within a post
    """
    sharesFilename=baseDir+'/accounts/'+nickname+'@'+domain+'/shares.json'
    sharesJson={}
    if os.path.isfile(sharesFilename):    
        with open(sharesFilename, 'r') as fp:
            sharesJson=commentjson.load(fp)

    duration=duration.lower()
    durationSec=0
    published=int(time.time())
    if ' ' in duration:
        durationList=duration.split(' ')
        if durationList[0].isdigit():
            if 'hour' in durationList[1]:
                durationSec=published+(int(durationList[0])*60*60)
            if 'day' in durationList[1]:
                durationSec=published+(int(durationList[0])*60*60*24)
            if 'week' in durationList[1]:
                durationSec=published+(int(durationList[0])*60*60*24*7)
            if 'month' in durationList[1]:
                durationSec=published+(int(durationList[0])*60*60*24*30)
            if 'year' in durationList[1]:
                durationSec=published+(int(durationList[0])*60*60*24*365)

    itemID=displayName.replace(' ','')

    # has an image for this share been uploaded?
    imageUrl=None
    moveImage=False
    if not imageFilename:
        sharesImageFilename=baseDir+'/accounts/'+nickname+'@'+domain+'/upload'
        if os.path.isfile(sharesImageFilename+'.png'):
            imageFilename=sharesImageFilename+'.png'
            moveImage=True
        elif os.path.isfile(sharesImageFilename+'.jpg'):
            imageFilename=sharesImageFilename+'.jpg'
            moveImage=True
        elif os.path.isfile(sharesImageFilename+'.gif'):
            imageFilename=sharesImageFilename+'.gif'
            moveImage=True

    # copy or move the image for the shared item to its destination
    if imageFilename:
        if os.path.isfile(imageFilename):
            domainFull=domain
            if port!=80 and port!=443:
                domainFull=domain+':'+str(port)
            if not os.path.isdir(baseDir+'/sharefiles'):
                os.mkdir(baseDir+'/sharefiles')
            if not os.path.isdir(baseDir+'/sharefiles/'+nickname):
                os.mkdir(baseDir+'/sharefiles/'+nickname)
            itemIDfile=baseDir+'/sharefiles/'+nickname+'/'+itemID
            if imageFilename.endswith('.png'):
                removeMetaData(imageFilename,itemIDfile+'.png')
                if moveImage:
                    os.remove(imageFilename)
                imageUrl=httpPrefix+'://'+domainFull+'/sharefiles/'+nickname+'/'+itemID+'.png'
            if imageFilename.endswith('.jpg'):
                removeMetaData(imageFilename,itemIDfile+'.jpg')
                if moveImage:
                    os.remove(imageFilename)
                imageUrl=httpPrefix+'://'+domainFull+'/sharefiles/'+nickname+'/'+itemID+'.jpg'
            if imageFilename.endswith('.gif'):
                removeMetaData(imageFilename,itemIDfile+'.gif')
                if moveImage:
                    os.remove(imageFilename)
                imageUrl=httpPrefix+'://'+domainFull+'/sharefiles/'+nickname+'/'+itemID+'.gif'

    sharesJson[itemID] = {
        "displayName": displayName,
        "summary": summary,
        "imageUrl": imageUrl,
        "itemType": itemType,
        "category": itemCategory,
        "location": location,
        "published": published,
        "expire": durationSec
    }

    with open(sharesFilename, 'w') as fp:
        commentjson.dump(sharesJson, fp, indent=4, sort_keys=True)

def expireShares(baseDir: str,nickname: str,domain: str) -> None:
    """Removes expired items from shares
    """
    handleDomain=domain
    if ':' in handleDomain:
        handleDomain=domain.split(':')[0]
    handle=nickname+'@'+handleDomain
    sharesFilename=baseDir+'/accounts/'+handle+'/shares.json'    
    if os.path.isfile(sharesFilename):
        with open(sharesFilename, 'r') as fp:
            sharesJson=commentjson.load(fp)
            currTime=int(time.time())
            deleteItemID=[]
            for itemID,item in sharesJson.items():
                if currTime>item['expire']:
                    deleteItemID.append(itemID)
            if deleteItemID:
                for itemID in deleteItemID:
                    del sharesJson[itemID]
                    # remove any associated images
                    itemIDfile=baseDir+'/sharefiles/'+nickname+'/'+itemID
                    if os.path.isfile(itemIDfile+'.png'):
                        os.remove(itemIDfile+'.png')
                    if os.path.isfile(itemIDfile+'.jpg'):
                        os.remove(itemIDfile+'.jpg')
                    if os.path.isfile(itemIDfile+'.gif'):
                        os.remove(itemIDfile+'.gif')
                with open(sharesFilename, 'w') as fp:
                    commentjson.dump(sharesJson, fp, indent=4, sort_keys=True)
        
def getSharesFeedForPerson(baseDir: str, \
                           domain: str,port: int, \
                           path: str,httpPrefix: str, \
                           sharesPerPage=12) -> {}:
    """Returns the shares for an account from GET requests
    """
    if '/shares' not in path:
        return None
    # handle page numbers
    headerOnly=True
    pageNumber=None    
    if '?page=' in path:
        pageNumber=path.split('?page=')[1]
        if pageNumber=='true':
            pageNumber=1
        else:
            try:
                pageNumber=int(pageNumber)
            except:
                pass
        path=path.split('?page=')[0]
        headerOnly=False
    
    if not path.endswith('/shares'):
        return None
    nickname=None
    if path.startswith('/users/'):
        nickname=path.replace('/users/','',1).replace('/shares','')
    if path.startswith('/@'):
        nickname=path.replace('/@','',1).replace('/shares','')
    if not nickname:
        return None
    if not validNickname(nickname):
        return None

    if port!=80 and port!=443:
        domain=domain+':'+str(port)

    handleDomain=domain
    if ':' in handleDomain:
        handleDomain=domain.split(':')[0]
    handle=nickname+'@'+handleDomain
    sharesFilename=baseDir+'/accounts/'+handle+'/shares.json'    

    if headerOnly:
        noOfShares=0
        if os.path.isfile(sharesFilename):
            with open(sharesFilename, 'r') as fp:
                sharesJson=commentjson.load(fp)
                noOfShares=len(sharesJson.items())
        shares = {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'first': httpPrefix+'://'+domain+'/users/'+nickname+'/shares?page=1',
            'id': httpPrefix+'://'+domain+'/users/'+nickname+'/shares',
            'totalItems': str(noOfShares),
            'type': 'OrderedCollection'}
        return shares

    if not pageNumber:
        pageNumber=1

    nextPageNumber=int(pageNumber+1)
    shares = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': httpPrefix+'://'+domain+'/users/'+nickname+'/shares?page='+str(pageNumber),
        'orderedItems': [],
        'partOf': httpPrefix+'://'+domain+'/users/'+nickname+'/shares',
        'totalItems': 0,
        'type': 'OrderedCollectionPage'}        

    if not os.path.isfile(sharesFilename):
        print("test5")
        return shares
    currPage=1
    pageCtr=0
    totalCtr=0

    with open(sharesFilename, 'r') as fp:
        sharesJson=commentjson.load(fp)
        for itemID,item in sharesJson.items():
            pageCtr += 1
            totalCtr += 1
            if currPage==pageNumber:
                shares['orderedItems'].append(item)
            if pageCtr>=sharesPerPage:
                pageCtr=0
                currPage += 1
    shares['totalItems']=totalCtr
    lastPage=int(totalCtr/sharesPerPage)
    if lastPage<1:
        lastPage=1
    if nextPageNumber>lastPage:
        shares['next']=httpPrefix+'://'+domain+'/users/'+nickname+'/shares?page='+str(lastPage)
    return shares

def sendShareViaServer(session,fromNickname: str,password: str,
                       fromDomain: str,fromPort: int, \
                       httpPrefix: str, \
                       displayName: str, \
                       summary: str, \
                       imageFilename: str, \
                       itemType: str, \
                       itemCategory: str, \
                       location: str, \
                       duration: str, \
                       cachedWebfingers: {},personCache: {}, \
                       debug: bool, \
                       projectVersion: str) -> {}:
    """Creates an item share via c2s
    """
    if not session:
        print('WARN: No session for sendShareViaServer')
        return 6

    fromDomainFull=fromDomain
    if fromPort!=80 and fromPort!=443:
        fromDomainFull=fromDomain+':'+str(fromPort)

    toUrl = 'https://www.w3.org/ns/activitystreams#Public'
    ccUrl = httpPrefix + '://'+fromDomainFull+'/users/'+fromNickname+'/followers'

    newShareJson = {
        'type': 'Add',
        'actor': httpPrefix+'://'+fromDomainFull+'/users/'+fromNickname,
        'target': httpPrefix+'://'+fromDomainFull+'/users/'+fromNickname+'/shares',
        'object': {
            "type": "Offer",
            "displayName": displayName,
            "summary": summary,
            "itemType": itemType,
            "category": category,
            "location": location,
            "duration": duration,
            'to': [toUrl],
            'cc': [ccUrl]
        },
        'to': [toUrl],
        'cc': [ccUrl]
    }

    handle=httpPrefix+'://'+fromDomainFull+'/@'+fromNickname

    # lookup the inbox for the To handle
    wfRequest = webfingerHandle(session,handle,httpPrefix,cachedWebfingers, \
                                fromDomain,projectVersion)
    if not wfRequest:
        if debug:
            print('DEBUG: announce webfinger failed for '+handle)
        return 1

    postToBox='outbox'

    # get the actor inbox for the To handle
    inboxUrl,pubKeyId,pubKey,fromPersonId,sharedInbox,capabilityAcquisition,avatarUrl,preferredName = \
        getPersonBox(session,wfRequest,personCache, \
                     projectVersion,httpPrefix,fromDomain,postToBox)
                     
    if not inboxUrl:
        if debug:
            print('DEBUG: No '+postToBox+' was found for '+handle)
        return 3
    if not fromPersonId:
        if debug:
            print('DEBUG: No actor was found for '+handle)
        return 4
    
    authHeader=createBasicAuthHeader(fromNickname,password)

    if imageFilename:
        headers = {'host': fromDomain, \
                   'Authorization': authHeader}
        postResult = \
            postImage(session,imageFilename,[],inboxUrl.replace('/'+postToBox,'/shares'),headers,"inbox:write")
    
    headers = {'host': fromDomain, \
               'Content-type': 'application/json', \
               'Authorization': authHeader}
    postResult = \
        postJson(session,newShareJson,[],inboxUrl,headers,"inbox:write")
    #if not postResult:
    #    if debug:
    #        print('DEBUG: POST announce failed for c2s to '+inboxUrl)
    #    return 5

    if debug:
        print('DEBUG: c2s POST share item success')

    return newShareJson

def sendUndoShareViaServer(session,fromNickname: str,password: str,
                           fromDomain: str,fromPort: int, \
                           httpPrefix: str, \
                           displayName: str, \
                           cachedWebfingers: {},personCache: {}, \
                           debug: bool,projectVersion: str) -> {}:
    """Undoes a share via c2s
    """
    if not session:
        print('WARN: No session for sendUndoShareViaServer')
        return 6

    fromDomainFull=fromDomain
    if fromPort!=80 and fromPort!=443:
        fromDomainFull=fromDomain+':'+str(fromPort)

    toUrl = 'https://www.w3.org/ns/activitystreams#Public'
    ccUrl = httpPrefix + '://'+fromDomainFull+'/users/'+fromNickname+'/followers'

    undoShareJson = {
        'type': 'Remove',
        'actor': httpPrefix+'://'+fromDomainFull+'/users/'+fromNickname,
        'target': httpPrefix+'://'+fromDomainFull+'/users/'+fromNickname+'/shares',
        'object': {
            "type": "Offer",
            "displayName": displayName,
            'to': [toUrl],
            'cc': [ccUrl]
        },
        'to': [toUrl],
        'cc': [ccUrl]
    }

    handle=httpPrefix+'://'+fromDomainFull+'/@'+fromNickname

    # lookup the inbox for the To handle
    wfRequest = webfingerHandle(session,handle,httpPrefix,cachedWebfingers, \
                                fromDomain,projectVersion)
    if not wfRequest:
        if debug:
            print('DEBUG: announce webfinger failed for '+handle)
        return 1

    postToBox='outbox'

    # get the actor inbox for the To handle
    inboxUrl,pubKeyId,pubKey,fromPersonId,sharedInbox,capabilityAcquisition,avatarUrl,preferredName = \
        getPersonBox(session,wfRequest,personCache, \
                     projectVersion,httpPrefix,fromDomain,postToBox)
                     
    if not inboxUrl:
        if debug:
            print('DEBUG: No '+postToBox+' was found for '+handle)
        return 3
    if not fromPersonId:
        if debug:
            print('DEBUG: No actor was found for '+handle)
        return 4
    
    authHeader=createBasicAuthHeader(fromNickname,password)
    
    headers = {'host': fromDomain, \
               'Content-type': 'application/json', \
               'Authorization': authHeader}
    postResult = \
        postJson(session,undoShareJson,[],inboxUrl,headers,"inbox:write")
    #if not postResult:
    #    if debug:
    #        print('DEBUG: POST announce failed for c2s to '+inboxUrl)
    #    return 5

    if debug:
        print('DEBUG: c2s POST undo share success')

    return undoShareJson

def outboxShareUpload(baseDir: str,httpPrefix: str, \
                      nickname: str,domain: str,port: int, \
                      messageJson: {},debug: bool) -> None:
    """ When a shared item is received by the outbox from c2s
    """
    if not messageJson.get('type'):
        return
    if not messageJson['type']=='Add':
        return
    if not messageJson.get('object'):
        return
    if not isinstance(messageJson['object'], dict):
        return
    if not messageJson['object'].get('type'):
        if debug:
            print('DEBUG: undo block - no type')
        return
    if not messageJson['object']['type']=='Offer':
        if debug:
            print('DEBUG: not an Offer activity')
        return
    if not messageJson['object'].get('displayName'):
        if debug:
            print('DEBUG: displayName missing from Offer')
        return
    if not messageJson['object'].get('summary'):
        if debug:
            print('DEBUG: summary missing from Offer')
        return
    if not messageJson['object'].get('itemType'):
        if debug:
            print('DEBUG: itemType missing from Offer')
        return
    if not messageJson['object'].get('category'):
        if debug:
            print('DEBUG: category missing from Offer')
        return
    if not messageJson['object'].get('location'):
        if debug:
            print('DEBUG: location missing from Offer')
        return
    if not messageJson['object'].get('duration'):
        if debug:
            print('DEBUG: duration missing from Offer')
        return
    addShare(baseDir, \
             httpPrefix,nickname,domain,port, \
             messageJson['object']['displayName'], \
             messageJson['object']['summary'], \
             messageJson['object']['imageFilename'], \
             messageJson['object']['itemType'], \
             messageJson['object']['itemCategory'], \
             messageJson['object']['location'], \
             messageJson['object']['duration'], \
             debug)
    if debug:
        print('DEBUG: shared item received via c2s')

def outboxUndoShareUpload(baseDir: str,httpPrefix: str, \
                          nickname: str,domain: str,port: int, \
                          messageJson: {},debug: bool) -> None:
    """ When a shared item is removed via c2s
    """
    if not messageJson.get('type'):
        return
    if not messageJson['type']=='Remove':
        return
    if not messageJson.get('object'):
        return
    if not isinstance(messageJson['object'], dict):
        return
    if not messageJson['object'].get('type'):
        if debug:
            print('DEBUG: undo block - no type')
        return
    if not messageJson['object']['type']=='Offer':
        if debug:
            print('DEBUG: not an Offer activity')
        return
    if not messageJson['object'].get('displayName'):
        if debug:
            print('DEBUG: displayName missing from Offer')
        return
    removeShare(baseDir,nickname,domain, \
                messageJson['object']['displayName'])
    if debug:
        print('DEBUG: shared item removed via c2s')
