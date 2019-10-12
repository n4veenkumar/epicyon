__filename__ = "like.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "1.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

import json
import time
import commentjson
from pprint import pprint
from utils import urlPermitted
from utils import getNicknameFromActor
from utils import getDomainFromActor
from utils import locatePost
from posts import sendSignedJson
from session import postJson
from webfinger import webfingerHandle
from auth import createBasicAuthHeader
from posts import getPersonBox

def undoLikesCollectionEntry(postFilename: str,objectUrl: str,actor: str,debug: bool) -> None:
    """Undoes a like for a particular actor
    """
    postJsonObject=None
    tries=0
    while tries<5:
        try:
            with open(postFilename, 'r') as fp:
                postJsonObject=commentjson.load(fp)
                break
        except Exception as e:
            print(e)
            time.sleep(1)
            tries+=1

    if postJsonObject:
        if not postJsonObject.get('type'):
            return
        if postJsonObject['type']!='Create':
            return
        if not postJsonObject.get('object'):
            if debug:
                pprint(postJsonObject)
                print('DEBUG: post '+objectUrl+' has no object')
            return
        if not isinstance(postJsonObject['object'], dict):
            return
        if not postJsonObject['object'].get('likes'):
            return
        if not isinstance(postJsonObject['object']['likes'], dict):
            return
        if not postJsonObject['object']['likes'].get('items'):
            return
        totalItems=0
        if postJsonObject['object']['likes'].get('totalItems'):
            totalItems=postJsonObject['object']['likes']['totalItems']
        itemFound=False
        for likeItem in postJsonObject['object']['likes']['items']:
            if likeItem.get('actor'):
                if likeItem['actor']==actor:
                    if debug:
                        print('DEBUG: like was removed for '+actor)
                    postJsonObject['object']['likes']['items'].remove(likeItem)
                    itemFound=True
                    break
        if itemFound:
            if totalItems==1:
                if debug:
                    print('DEBUG: likes was removed from post')
                del postJsonObject['object']['likes']
            else:
                postJsonObject['object']['likes']['totalItems']=len(postJsonObject['likes']['items'])
            tries=0
            while tries<5:
                try:
                    with open(postFilename, 'w') as fp:
                        commentjson.dump(postJsonObject, fp, indent=4, sort_keys=False)
                        break
                except Exception as e:
                    print(e)
                    time.sleep(1)
                    tries+=1

def likedByPerson(postJsonObject: {}, nickname: str,domain: str) -> bool:
    """Returns True if the given post is liked by the given person
    """
    if noOfLikes(postJsonObject)==0:
        return False
    actorMatch=domain+'/users/'+nickname
    for item in postJsonObject['object']['likes']['items']:
        if item['actor'].endswith(actorMatch):
            return True
    return False

def noOfLikes(postJsonObject: {}) -> int:
    """Returns the number of likes ona  given post
    """
    if not postJsonObject.get('object'):
        return 0
    if not isinstance(postJsonObject['object'], dict):
        return 0
    if not postJsonObject['object'].get('likes'):
        return 0
    if not isinstance(postJsonObject['object']['likes'], dict):
        return 0
    if not postJsonObject['object']['likes'].get('items'):
        postJsonObject['object']['likes']['items']=[]
        postJsonObject['object']['likes']['totalItems']=0
    return len(postJsonObject['object']['likes']['items'])

def updateLikesCollection(postFilename: str,objectUrl: str, actor: str,debug: bool) -> None:
    """Updates the likes collection within a post
    """
    postJsonObject=None
    tries=0
    while tries<5:
        try:
            with open(postFilename, 'r') as fp:
                postJsonObject=commentjson.load(fp)
                break
        except Exception as e:
            print(e)
            time.sleep(1)
            tries+=1

    if postJsonObject:
        if not postJsonObject.get('object'):
            if debug:
                pprint(postJsonObject)
                print('DEBUG: post '+objectUrl+' has no object')
            return
        if not objectUrl.endswith('/likes'):
            objectUrl=objectUrl+'/likes'
        if not postJsonObject['object'].get('likes'):
            if debug:
                print('DEBUG: Adding initial likes to '+objectUrl)
            likesJson = {
                "@context": "https://www.w3.org/ns/activitystreams",
                'id': objectUrl,
                'type': 'Collection',
                "totalItems": 1,
                'items': [{
                    'type': 'Like',
                    'actor': actor
                }]                
            }
            postJsonObject['object']['likes']=likesJson
        else:
            if not postJsonObject['object']['likes'].get('items'):
                postJsonObject['object']['likes']['items']=[]
            for likeItem in postJsonObject['object']['likes']['items']:
                if likeItem.get('actor'):
                    if likeItem['actor']==actor:
                        return
            newLike={
                'type': 'Like',
                'actor': actor
            }
            postJsonObject['object']['likes']['items'].append(newLike)
            postJsonObject['object']['likes']['totalItems']=len(postJsonObject['object']['likes']['items'])

        if debug:
            print('DEBUG: saving post with likes added')
            pprint(postJsonObject)
        tries=0
        while tries<5:
            try:
                with open(postFilename, 'w') as fp:
                    commentjson.dump(postJsonObject, fp, indent=4, sort_keys=False)
                    break
            except Exception as e:
                print(e)
                time.sleep(1)
                tries+=1

def like(session,baseDir: str,federationList: [],nickname: str,domain: str,port: int, \
         ccList: [],httpPrefix: str,objectUrl: str,clientToServer: bool, \
         sendThreads: [],postLog: [],personCache: {},cachedWebfingers: {}, \
         debug: bool,projectVersion: str) -> {}:
    """Creates a like
    actor is the person doing the liking
    'to' might be a specific person (actor) whose post was liked
    object is typically the url of the message which was liked
    """
    if not urlPermitted(objectUrl,federationList,"inbox:write"):
        return None

    fullDomain=domain
    if port:
        if port!=80 and port!=443:
            if ':' not in domain:
                fullDomain=domain+':'+str(port)

    likeTo=[]
    if '/statuses/' in objectUrl:
        likeTo=[objectUrl.split('/statuses/')[0]]

    newLikeJson = {
        "@context": "https://www.w3.org/ns/activitystreams",
        'type': 'Like',
        'actor': httpPrefix+'://'+fullDomain+'/users/'+nickname,
        'object': objectUrl
    }
    if ccList:
        if len(ccList)>0:
            newLikeJson['cc']=ccList

    # Extract the domain and nickname from a statuses link
    likedPostNickname=None
    likedPostDomain=None
    likedPostPort=None
    if '/users/' in objectUrl or '/profile/' in objectUrl:
        likedPostNickname=getNicknameFromActor(objectUrl)
        likedPostDomain,likedPostPort=getDomainFromActor(objectUrl)

    if likedPostNickname:
        postFilename=locatePost(baseDir,nickname,domain,objectUrl)
        if not postFilename:
            print('DEBUG: like baseDir: '+baseDir)
            print('DEBUG: like nickname: '+nickname)
            print('DEBUG: like domain: '+domain)
            print('DEBUG: like objectUrl: '+objectUrl)
            return None
        
        updateLikesCollection(postFilename,objectUrl,newLikeJson['actor'],debug)
        
        sendSignedJson(newLikeJson,session,baseDir, \
                       nickname,domain,port, \
                       likedPostNickname,likedPostDomain,likedPostPort, \
                       'https://www.w3.org/ns/activitystreams#Public', \
                       httpPrefix,True,clientToServer,federationList, \
                       sendThreads,postLog,cachedWebfingers,personCache, \
                       debug,projectVersion)

    return newLikeJson

def likePost(session,baseDir: str,federationList: [], \
             nickname: str,domain: str,port: int,httpPrefix: str, \
             likeNickname: str,likeDomain: str,likePort: int, \
             ccList: [], \
             likeStatusNumber: int,clientToServer: bool, \
             sendThreads: [],postLog: [], \
             personCache: {},cachedWebfingers: {}, \
             debug: bool,projectVersion: str) -> {}:
    """Likes a given status post
    """
    likeDomain=likeDomain
    if likePort:
        if likePort!=80 and likePort!=443:
            if ':' not in likeDomain:
                likeDomain=likeDomain+':'+str(likePort)

    objectUrl = \
        httpPrefix + '://'+likeDomain+'/users/'+likeNickname+ \
        '/statuses/'+str(likeStatusNumber)

    ccUrl=httpPrefix+'://'+likeDomain+'/users/'+likeNickname
    if likePort:
        if likePort!=80 and likePort!=443:
            if ':' not in likeDomain:
                ccUrl=httpPrefix+'://'+likeDomain+':'+str(likePort)+'/users/'+likeNickname
        
    return like(session,baseDir,federationList,nickname,domain,port, \
                ccList,httpPrefix,objectUrl,clientToServer, \
                sendThreads,postLog,personCache,cachedWebfingers, \
                debug,projectVersion)

def undolike(session,baseDir: str,federationList: [],nickname: str,domain: str,port: int, \
             ccList: [],httpPrefix: str,objectUrl: str,clientToServer: bool, \
             sendThreads: [],postLog: [],personCache: {},cachedWebfingers: {}, \
             debug: bool,projectVersion: str) -> {}:
    """Removes a like
    actor is the person doing the liking
    'to' might be a specific person (actor) whose post was liked
    object is typically the url of the message which was liked
    """
    if not urlPermitted(objectUrl,federationList,"inbox:write"):
        return None

    fullDomain=domain
    if port:
        if port!=80 and port!=443:
            if ':' not in domain:
                fullDomain=domain+':'+str(port)

    likeTo=[]
    if '/statuses/' in objectUrl:
        likeTo=[objectUrl.split('/statuses/')[0]]

    newUndoLikeJson = {
        "@context": "https://www.w3.org/ns/activitystreams",
        'type': 'Undo',
        'actor': httpPrefix+'://'+fullDomain+'/users/'+nickname,
        'object': {
            'type': 'Like',
            'actor': httpPrefix+'://'+fullDomain+'/users/'+nickname,
            'object': objectUrl
        }
    }
    if ccList:
        if len(ccList)>0:
            newUndoLikeJson['cc']=ccList
            newUndoLikeJson['object']['cc']=ccList

    # Extract the domain and nickname from a statuses link
    likedPostNickname=None
    likedPostDomain=None
    likedPostPort=None
    if '/users/' in objectUrl or '/profile/' in objectUrl:
        likedPostNickname=getNicknameFromActor(objectUrl)
        likedPostDomain,likedPostPort=getDomainFromActor(objectUrl)

    if likedPostNickname:
        postFilename=locatePost(baseDir,nickname,domain,objectUrl)
        if not postFilename:
            return None

        undoLikesCollectionEntry(postFilename,objectUrl,newLikeJson['actor'],debug)
        
        sendSignedJson(newUndoLikeJson,session,baseDir, \
                       nickname,domain,port, \
                       likedPostNickname,likedPostDomain,likedPostPort, \
                       'https://www.w3.org/ns/activitystreams#Public', \
                       httpPrefix,True,clientToServer,federationList, \
                       sendThreads,postLog,cachedWebfingers,personCache, \
                       debug,projectVersion)
    else:
        return None

    return newUndoLikeJson

def undoLikePost(session,baseDir: str,federationList: [], \
                 nickname: str,domain: str,port: int,httpPrefix: str, \
                 likeNickname: str,likeDomain: str,likePort: int, \
                 ccList: [], \
                 likeStatusNumber: int,clientToServer: bool, \
                 sendThreads: [],postLog: [], \
                 personCache: {},cachedWebfingers: {}, \
                 debug: bool) -> {}:
    """Removes a liked post
    """
    likeDomain=likeDomain
    if likePort:
        if likePort!=80 and likePort!=443:
            if ':' not in likeDomain:
                likeDomain=likeDomain+':'+str(likePort)

    objectUrl = \
        httpPrefix + '://'+likeDomain+'/users/'+likeNickname+ \
        '/statuses/'+str(likeStatusNumber)

    ccUrl=httpPrefix+'://'+likeDomain+'/users/'+likeNickname
    if likePort:
        if likePort!=80 and likePort!=443:
            if ':' not in likeDomain:
                ccUrl=httpPrefix+'://'+likeDomain+':'+str(likePort)+'/users/'+likeNickname
        
    return undoLike(session,baseDir,federationList,nickname,domain,port, \
                    ccList,httpPrefix,objectUrl,clientToServer, \
                    sendThreads,postLog,personCache,cachedWebfingers,debug)

def sendLikeViaServer(baseDir: str,session, \
                      fromNickname: str,password: str,
                      fromDomain: str,fromPort: int, \
                      httpPrefix: str,likeUrl: str, \
                      cachedWebfingers: {},personCache: {}, \
                      debug: bool,projectVersion: str) -> {}:
    """Creates a like via c2s
    """
    if not session:
        print('WARN: No session for sendLikeViaServer')
        return 6

    fromDomainFull=fromDomain
    if fromPort:
        if fromPort!=80 and fromPort!=443:
            if ':' not in fromDomain:
                fromDomainFull=fromDomain+':'+str(fromPort)

    toUrl = ['https://www.w3.org/ns/activitystreams#Public']
    ccUrl = httpPrefix + '://'+fromDomainFull+'/users/'+fromNickname+'/followers'

    if '/statuses/' in likeUrl:
        toUrl=[likeUrl.split('/statuses/')[0]]
    
    newLikeJson = {
        "@context": "https://www.w3.org/ns/activitystreams",
        'type': 'Like',
        'actor': httpPrefix+'://'+fromDomainFull+'/users/'+fromNickname,
        'object': likeUrl
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
    inboxUrl,pubKeyId,pubKey,fromPersonId,sharedInbox,capabilityAcquisition,avatarUrl,displayName = \
        getPersonBox(baseDir,session,wfRequest,personCache, \
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
        postJson(session,newLikeJson,[],inboxUrl,headers,"inbox:write")
    #if not postResult:
    #    if debug:
    #        print('DEBUG: POST announce failed for c2s to '+inboxUrl)
    #    return 5

    if debug:
        print('DEBUG: c2s POST like success')

    return newLikeJson

def sendUndoLikeViaServer(baseDir: str,session, \
                          fromNickname: str,password: str, \
                          fromDomain: str,fromPort: int, \
                          httpPrefix: str,likeUrl: str, \
                          cachedWebfingers: {},personCache: {}, \
                          debug: bool,projectVersion: str) -> {}:
    """Undo a like via c2s
    """
    if not session:
        print('WARN: No session for sendUndoLikeViaServer')
        return 6

    fromDomainFull=fromDomain
    if fromPort:
        if fromPort!=80 and fromPort!=443:
            if ':' not in fromDomain:
                fromDomainFull=fromDomain+':'+str(fromPort)

    toUrl = ['https://www.w3.org/ns/activitystreams#Public']
    ccUrl = httpPrefix + '://'+fromDomainFull+'/users/'+fromNickname+'/followers'

    if '/statuses/' in likeUrl:
        toUrl=[likeUrl.split('/statuses/')[0]]

    newUndoLikeJson = {
        "@context": "https://www.w3.org/ns/activitystreams",
        'type': 'Undo',
        'actor': httpPrefix+'://'+fromDomainFull+'/users/'+fromNickname,
        'object': {
            'type': 'Like',
            'actor': httpPrefix+'://'+fromDomainFull+'/users/'+fromNickname,
            'object': likeUrl
        }
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
    inboxUrl,pubKeyId,pubKey,fromPersonId,sharedInbox,capabilityAcquisition,avatarUrl,displayName = \
        getPersonBox(baseDir,session,wfRequest,personCache, \
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
        postJson(session,newUndoLikeJson,[],inboxUrl,headers,"inbox:write")
    #if not postResult:
    #    if debug:
    #        print('DEBUG: POST announce failed for c2s to '+inboxUrl)
    #    return 5

    if debug:
        print('DEBUG: c2s POST undo like success')

    return newUndoLikeJson

def outboxLike(baseDir: str,httpPrefix: str, \
               nickname: str,domain: str,port: int, \
               messageJson: {},debug: bool) -> None:
    """ When a like request is received by the outbox from c2s
    """
    if not messageJson.get('type'):
        if debug:
            print('DEBUG: like - no type')
        return
    if not messageJson['type']=='Like':
        if debug:
            print('DEBUG: not a like')
        return
    if not messageJson.get('object'):
        if debug:
            print('DEBUG: no object in like')
        return
    if not isinstance(messageJson['object'], str):
        if debug:
            print('DEBUG: like object is not string')
        return
    if debug:
        print('DEBUG: c2s like request arrived in outbox')

    messageId=messageJson['object'].replace('/activity','')
    if '/statuses/' not in messageId:
        if debug:
            print('DEBUG: c2s like object is not a status')
        return
    if '/users/' not in messageId and '/profile/' not in messageId:
        if debug:
            print('DEBUG: c2s like object has no nickname')
        return
    if ':' in domain:
        domain=domain.split(':')[0]
    postFilename=locatePost(baseDir,nickname,domain,messageId)
    if not postFilename:
        if debug:
            print('DEBUG: c2s like post not found in inbox or outbox')
            print(messageId)
        return True
    updateLikesCollection(postFilename,messageId,messageJson['actor'],debug)
    if debug:
        print('DEBUG: post liked via c2s - '+postFilename)

def outboxUndoLike(baseDir: str,httpPrefix: str, \
                   nickname: str,domain: str,port: int, \
                   messageJson: {},debug: bool) -> None:
    """ When an undo like request is received by the outbox from c2s
    """
    if not messageJson.get('type'):
        return
    if not messageJson['type']=='Undo':
        return
    if not messageJson.get('object'):
        return
    if not isinstance(messageJson['object'], dict):
        if debug:
            print('DEBUG: undo like object is not dict')
        return    
    if not messageJson['object'].get('type'):
        if debug:
            print('DEBUG: undo like - no type')
        return
    if not messageJson['object']['type']=='Like':
        if debug:
            print('DEBUG: not a undo like')
        return
    if not messageJson['object'].get('object'):
        if debug:
            print('DEBUG: no object in undo like')
        return
    if not isinstance(messageJson['object']['object'], str):
        if debug:
            print('DEBUG: undo like object is not string')
        return
    if debug:
        print('DEBUG: c2s undo like request arrived in outbox')

    messageId=messageJson['object']['object'].replace('/activity','')
    if '/statuses/' not in messageId:
        if debug:
            print('DEBUG: c2s undo like object is not a status')
        return
    if '/users/' not in messageId and '/profile/' not in messageId:
        if debug:
            print('DEBUG: c2s undo like object has no nickname')
        return
    if ':' in domain:
        domain=domain.split(':')[0]
    postFilename=locatePost(baseDir,nickname,domain,messageId)
    if not postFilename:
        if debug:
            print('DEBUG: c2s undo like post not found in inbox or outbox')
            print(messageId)
        return True
    undoLikesCollectionEntry(postFilename,messageId,messageJson['actor'],debug)
    if debug:
        print('DEBUG: post undo liked via c2s - '+postFilename)
