__filename__ = "daemon.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "0.0.1"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
#import socketserver
import commentjson
import json
import time
from hashlib import sha256
from pprint import pprint
from session import createSession
from webfinger import webfingerMeta
from webfinger import webfingerLookup
from webfinger import webfingerHandle
from person import personLookup
from person import personBoxJson
from person import createSharedInbox
from posts import outboxMessageCreateWrap
from posts import savePostToBox
from posts import sendToFollowers
from posts import postIsAddressedToPublic
from posts import sendToNamedAddresses
from inbox import inboxPermittedMessage
from inbox import inboxMessageHasParams
from inbox import runInboxQueue
from inbox import savePostToInboxQueue
from follow import getFollowingFeed
from follow import outboxUndoFollow
from auth import authorize
from auth import createPassword
from auth import createBasicAuthHeader
from auth import authorizeBasic
from threads import threadWithTrace
from media import getMediaPath
from media import createMediaDirs
from delete import outboxDelete
from like import outboxLike
from like import outboxUndoLike
from blocking import outboxBlock
from blocking import outboxUndoBlock
from config import setConfigParam
from roles import outboxDelegate
from skills import outboxSkills
from availability import outboxAvailability
from webinterface import htmlIndividualPost
from webinterface import htmlProfile
from webinterface import htmlInbox
from webinterface import htmlOutbox
from webinterface import htmlPostReplies
from webinterface import htmlLogin
from webinterface import htmlGetLoginCredentials
from shares import getSharesFeedForPerson
from shares import outboxShareUpload
from shares import outboxUndoShareUpload
import os
import sys

# maximum number of posts to list in outbox feed
maxPostsInFeed=20

# number of follows/followers per page
followsPerPage=12

# number of item shares per page
sharesPerPage=12

def readFollowList(filename: str):
    """Returns a list of ActivityPub addresses to follow
    """
    followlist=[]
    if not os.path.isfile(filename):
        return followlist
    followUsers = open(filename, "r")    
    for u in followUsers:
        if u not in followlist:
            nickname,domain = parseHandle(u)
            if nickname:
                followlist.append(nickname+'@'+domain)
    followUsers.close()
    return followlist

class PubServer(BaseHTTPRequestHandler):
    def _login_headers(self,fileFormat: str) -> None:            
        self.send_response(200)
        self.send_header('Content-type', fileFormat)
        self.send_header('Host', self.server.domainFull)
        self.send_header('WWW-Authenticate', 'title="Login to Epicyon", Basic realm="epicyon"')
        self.end_headers()

    def _set_headers(self,fileFormat: str) -> None:
        self.send_response(200)
        self.send_header('Content-type', fileFormat)
        self.send_header('Host', self.server.domainFull)
        self.end_headers()

    def _404(self) -> None:
        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("<html><head></head><body><h1>404 Not Found</h1></body></html>".encode('utf-8'))

    def _webfinger(self) -> bool:
        if not self.path.startswith('/.well-known'):
            return False
        if self.server.debug:
            print('DEBUG: WEBFINGER well-known')

        if self.server.debug:
            print('DEBUG: WEBFINGER host-meta')
        if self.path.startswith('/.well-known/host-meta'):
            wfResult=webfingerMeta()
            if wfResult:
                self._set_headers('application/xrd+xml')
                self.wfile.write(wfResult.encode('utf-8'))
            return

        if self.server.debug:
            print('DEBUG: WEBFINGER lookup '+self.path+' '+str(self.server.baseDir))
        wfResult=webfingerLookup(self.path,self.server.baseDir,self.server.port,self.server.debug)
        if wfResult:
            self._set_headers('application/jrd+json')
            self.wfile.write(json.dumps(wfResult).encode('utf-8'))
        else:
            if self.server.debug:
                print('DEBUG: WEBFINGER lookup 404 '+self.path)
            self._404()
        return True

    def _permittedDir(self,path: str) -> bool:
        """These are special paths which should not be accessible
        directly via GET or POST
        """
        if path.startswith('/wfendpoints') or \
           path.startswith('/keys') or \
           path.startswith('/accounts'):
            return False
        return True

    def _postToOutbox(self,messageJson: {}) -> bool:
        """post is received by the outbox
        Client to server message post
        https://www.w3.org/TR/activitypub/#client-to-server-outbox-delivery
        """
        if not messageJson.get('type'):
            if self.server.debug:
                print('DEBUG: POST to outbox has no "type" parameter')
            return False
        if not messageJson.get('object') and messageJson.get('content'):
            if messageJson['type']!='Create':
                # https://www.w3.org/TR/activitypub/#object-without-create
                if self.server.debug:
                    print('DEBUG: POST to outbox - adding Create wrapper')
                messageJson= \
                    outboxMessageCreateWrap(self.server.httpPrefix, \
                                            self.postToNickname, \
                                            self.server.domain, \
                                            self.server.port, \
                                            messageJson)
        if messageJson['type']=='Create':
            if not (messageJson.get('id') and \
                    messageJson.get('type') and \
                    messageJson.get('actor') and \
                    messageJson.get('object') and \
                    messageJson.get('to')):
                if self.server.debug:
                    pprint(messageJson)
                    print('DEBUG: POST to outbox - Create does not have the required parameters')
                return False
            # https://www.w3.org/TR/activitypub/#create-activity-outbox
            messageJson['object']['attributedTo']=messageJson['actor']
            if messageJson['object'].get('attachment'):
                attachmentIndex=0
                if messageJson['object']['attachment'][attachmentIndex].get('mediaType'):
                    fileExtension='png'
                    if messageJson['object']['attachment'][attachmentIndex]['mediaType'].endswith('jpeg'):
                        fileExtension='jpg'
                    if messageJson['object']['attachment'][attachmentIndex]['mediaType'].endswith('gif'):
                        fileExtension='gif'
                    mediaDir=self.server.baseDir+'/accounts/'+self.postToNickname+'@'+self.server.domain
                    uploadMediaFilename=mediaDir+'/upload.'+fileExtension
                    if not os.path.isfile(uploadMediaFilename):
                        del messageJson['object']['attachment']
                    else:
                        # generate a path for the uploaded image
                        mPath=getMediaPath()
                        mediaPath=mPath+'/'+createPassword(32)+'.'+fileExtension
                        createMediaDirs(self.server.baseDir,mPath)
                        mediaFilename=self.server.baseDir+'/'+mediaPath
                        # move the uploaded image to its new path
                        os.rename(uploadMediaFilename,mediaFilename)
                        # change the url of the attachment
                        messageJson['object']['attachment'][attachmentIndex]['url']= \
                            self.server.httpPrefix+'://'+self.server.domain+'/'+mediaPath
                
        permittedOutboxTypes=[
            'Create','Announce','Like','Follow','Undo', \
            'Update','Add','Remove','Block','Delete', \
            'Delegate','Skill'
        ]
        if messageJson['type'] not in permittedOutboxTypes:
            if self.server.debug:
                print('DEBUG: POST to outbox - '+messageJson['type']+ \
                      ' is not a permitted activity type')
            return False
        if messageJson.get('id'):
            postId=messageJson['id'].replace('/activity','')
            if self.server.debug:
                print('DEBUG: id attribute exists within POST to outbox')
        else:
            if self.server.debug:
                print('DEBUG: No id attribute within POST to outbox')
            postId=None
        if self.server.debug:
            pprint(messageJson)
            print('DEBUG: savePostToBox')
        domainFull=self.server.domain
        if self.server.port!=80 and self.server.port!=443:
            domainFull=self.server.domain+':'+str(self.server.port)
        savePostToBox(self.server.baseDir, \
                      self.server.httpPrefix, \
                      postId, \
                      self.postToNickname, \
                      domainFull,messageJson,'outbox')
        if not self.server.session:
            if self.server.debug:
                print('DEBUG: creating new session for c2s')
            self.server.session= \
                createSession(self.server.domain,self.server.port,self.server.useTor)
        if self.server.debug:
            print('DEBUG: sending c2s post to followers')
        sendToFollowers(self.server.session,self.server.baseDir, \
                        self.postToNickname,self.server.domain, \
                        self.server.port, \
                        self.server.httpPrefix, \
                        self.server.federationList, \
                        self.server.sendThreads, \
                        self.server.postLog, \
                        self.server.cachedWebfingers, \
                        self.server.personCache, \
                        messageJson,self.server.debug)
        if self.server.debug:
            print('DEBUG: handle any unfollow requests')
        outboxUndoFollow(self.server.baseDir,messageJson,self.server.debug)
        if self.server.debug:
            print('DEBUG: handle delegation requests')
        outboxDelegate(self.server.baseDir,self.postToNickname,messageJson,self.server.debug)
        if self.server.debug:
            print('DEBUG: handle skills changes requests')
        outboxSkills(self.server.baseDir,self.postToNickname,messageJson,self.server.debug)
        if self.server.debug:
            print('DEBUG: handle availability changes requests')
        outboxAvailability(self.server.baseDir,self.postToNickname,messageJson,self.server.debug)
        if self.server.debug:
            print('DEBUG: handle any like requests')
        outboxLike(self.server.baseDir,self.server.httpPrefix, \
                   self.postToNickname,self.server.domain,self.server.port, \
                   messageJson,self.server.debug)
        if self.server.debug:
            print('DEBUG: handle any undo like requests')
        outboxUndoLike(self.server.baseDir,self.server.httpPrefix, \
                       self.postToNickname,self.server.domain,self.server.port, \
                       messageJson,self.server.debug)
        if self.server.debug:
            print('DEBUG: handle delete requests')
        outboxDelete(self.server.baseDir,self.server.httpPrefix, \
                     self.postToNickname,self.server.domain, \
                     messageJson,self.server.debug)
        if self.server.debug:
            print('DEBUG: handle block requests')
        outboxBlock(self.server.baseDir,self.server.httpPrefix, \
                    self.postToNickname,self.server.domain, \
                    self.server.port,
                    messageJson,self.server.debug)
        if self.server.debug:
            print('DEBUG: handle undo block requests')
        outboxUndoBlock(self.server.baseDir,self.server.httpPrefix, \
                        self.postToNickname,self.server.domain, \
                        self.server.port,
                        messageJson,self.server.debug)
        if self.server.debug:
            print('DEBUG: handle share uploads')
        outboxShareUpload(self.server.baseDir,self.server.httpPrefix, \
                          self.postToNickname,self.server.domain, \
                          self.server.port,
                          messageJson,self.server.debug)
        if self.server.debug:
            print('DEBUG: handle undo share uploads')
        outboxUndoShareUpload(self.server.baseDir,self.server.httpPrefix, \
                              self.postToNickname,self.server.domain, \
                              self.server.port,
                              messageJson,self.server.debug)
        if self.server.debug:
            print('DEBUG: sending c2s post to named addresses')
            print('c2s sender: '+self.postToNickname+'@'+self.server.domain+':'+str(self.server.port))
        sendToNamedAddresses(self.server.session,self.server.baseDir, \
                             self.postToNickname,self.server.domain, \
                             self.server.port, \
                             self.server.httpPrefix, \
                             self.server.federationList, \
                             self.server.sendThreads, \
                             self.server.postLog, \
                             self.server.cachedWebfingers, \
                             self.server.personCache, \
                             messageJson,self.server.debug)
        return True

    def _updateInboxQueue(self,nickname: str,messageJson: {}) -> int:
        """Update the inbox queue
        """
        # Check if the queue is full
        if len(self.server.inboxQueue)>=self.server.maxQueueLength:
            return 1

        domainFull=self.server.domain
        if self.server.port!=80 and self.server.port!=443:
            domainFull=self.server.domain+':'+str(self.server.port)
        
        # save the json for later queue processing            
        queueFilename = \
            savePostToInboxQueue(self.server.baseDir, \
                                 self.server.httpPrefix, \
                                 nickname, \
                                 domainFull, \
                                 messageJson,
                                 self.headers['host'],
                                 self.headers['signature'],
                                 '/'+self.path.split('/')[-1],
                                 self.server.debug)
        if queueFilename:
            # add json to the queue
            if queueFilename not in self.server.inboxQueue:
                self.server.inboxQueue.append(queueFilename)
            self.send_response(201)
            self.end_headers()
            self.server.POSTbusy=False
            return 0
        return 2

    def _isAuthorized(self) -> bool:
        # token based authenticated used by the web interface
        if self.headers.get('Cookie'):
            if '=' in self.headers['Cookie']:
                tokenStr=self.headers['Cookie'].split('=',1)[1]
                if self.server.tokensLookup.get(tokenStr):
                    nickname=self.server.tokensLookup[tokenStr]
                    if '/'+nickname+'/' in self.path:
                        return True
                    if self.path.endswith('/'+nickname):
                        return True
            return False
        # basic auth
        if self.headers.get('Authorization'):
            if authorize(self.server.baseDir,self.path, \
                         self.headers['Authorization'], \
                         self.server.debug):
                return True
        return False
    
    def do_GET(self):        
        if self.server.debug:
            print('DEBUG: GET from '+self.server.baseDir+ \
                  ' path: '+self.path+' busy: '+ \
                  str(self.server.GETbusy))

        if self.server.debug:
            print(str(self.headers))

        # check authorization
        authorized = self._isAuthorized()
        if authorized:
            if self.server.debug:
                print('GET Authorization granted')
        else:
            if self.server.debug:
                print('GET Not authorized')

        # if not authorized then show the login screen
        if self.headers.get('Accept'):
            if 'text/html' in self.headers['Accept'] and self.path!='/login':
                if '/media/' not in self.path and 'sharefiles' not in self.path:
                    if not authorized:
                        self.send_response(303)
                        self.send_header('Location', '/login')
                        self.end_headers()
                        self.server.POSTbusy=False
                        return
            
        # get css
        # Note that this comes before the busy flag to avoid conflicts
        if self.path.endswith('.css'):
            if os.path.isfile('epicyon-profile.css'):
                with open('epicyon-profile.css', 'r') as cssfile:
                    css = cssfile.read()
                self._set_headers('text/css')
                self.wfile.write(css.encode('utf-8'))
                return
        # image on login screen
        if self.path=='/login.png':
            mediaFilename= \
                self.server.baseDir+'/accounts/login.png'
            if os.path.isfile(mediaFilename):
                self._set_headers('image/png')
                with open(mediaFilename, 'rb') as avFile:
                    mediaBinary = avFile.read()
                    self.wfile.write(mediaBinary)
            return        
        # show media
        # Note that this comes before the busy flag to avoid conflicts
        if '/media/' in self.path:
            if self.path.endswith('.png') or \
               self.path.endswith('.jpg') or \
               self.path.endswith('.gif'):
                mediaStr=self.path.split('/media/')[1]
                mediaFilename= \
                    self.server.baseDir+'/media/'+mediaStr
                if os.path.isfile(mediaFilename):
                    if mediaFilename.endswith('.png'):
                        self._set_headers('image/png')
                    elif mediaFilename.endswith('.jpg'):
                        self._set_headers('image/jpeg')
                    else:
                        self._set_headers('image/gif')
                    with open(mediaFilename, 'rb') as avFile:
                        mediaBinary = avFile.read()
                        self.wfile.write(mediaBinary)
                    return        
            self._404()
            return
        # show shared item images
        # Note that this comes before the busy flag to avoid conflicts
        if '/sharefiles/' in self.path:
            if self.path.endswith('.png') or \
               self.path.endswith('.jpg') or \
               self.path.endswith('.gif'):
                mediaStr=self.path.split('/sharefiles/')[1]
                mediaFilename= \
                    self.server.baseDir+'/sharefiles/'+mediaStr
                if os.path.isfile(mediaFilename):
                    if mediaFilename.endswith('.png'):
                        self._set_headers('image/png')
                    elif mediaFilename.endswith('.jpg'):
                        self._set_headers('image/jpeg')
                    else:
                        self._set_headers('image/gif')
                    with open(mediaFilename, 'rb') as avFile:
                        mediaBinary = avFile.read()
                        self.wfile.write(mediaBinary)
                    return        
            self._404()
            return
        # show avatar or background image
        # Note that this comes before the busy flag to avoid conflicts
        if '/users/' in self.path:
            if self.path.endswith('.png') or \
               self.path.endswith('.jpg') or \
               self.path.endswith('.gif'):
                avatarStr=self.path.split('/users/')[1]
                if '/' in avatarStr:
                    avatarNickname=avatarStr.split('/')[0]
                    avatarFile=avatarStr.split('/')[1]
                    avatarFilename= \
                        self.server.baseDir+'/accounts/'+ \
                        avatarNickname+'@'+ \
                        self.server.domain+'/'+avatarFile
                    if os.path.isfile(avatarFilename):
                        if avatarFile.endswith('.png'):
                            self._set_headers('image/png')
                        elif avatarFile.endswith('.jpg'):
                            self._set_headers('image/jpeg')
                        else:
                            self._set_headers('image/gif')
                        with open(avatarFilename, 'rb') as avFile:
                            avBinary = avFile.read()
                            self.wfile.write(avBinary)
                        return

        # This busy state helps to avoid flooding
        # Resources which are expected to be called from a web page
        # should be above this
        if self.server.GETbusy:
            currTimeGET=int(time.time())
            if currTimeGET-self.server.lastGET<10:
                if self.server.debug:
                    print('DEBUG: GET Busy')
                self.send_response(429)                    
                self.end_headers()
                return
            self.server.lastGET=currTimeGET
        self.server.GETbusy=True

        if not self._permittedDir(self.path):
            if self.server.debug:
                print('DEBUG: GET Not permitted')
            self._404()
            self.server.GETbusy=False
            return
        # get webfinger endpoint for a person
        if self._webfinger():
            self.server.GETbusy=False
            return
        
        if self.path.startswith('/login'):
            # request basic auth
            self._login_headers('text/html')
            self.wfile.write(htmlLogin(self.server.baseDir).encode('utf-8'))
            self.server.GETbusy=False
            return        

        # get an individual post from the path /@nickname/statusnumber
        if '/@' in self.path:
            namedStatus=self.path.split('/@')[1]
            if '/' not in namedStatus:
                # show actor
                nickname=namedStatus
            else:
                postSections=namedStatus.split('/')
                if len(postSections)==2:
                    nickname=postSections[0]
                    statusNumber=postSections[1]
                    if len(statusNumber)>10 and statusNumber.isdigit():
                        postFilename= \
                            self.server.baseDir+'/accounts/'+nickname+'@'+self.server.domain+'/outbox/'+ \
                            self.server.httpPrefix+':##'+self.server.domainFull+'#users#'+nickname+'#statuses#'+statusNumber+'.json'
                        if os.path.isfile(postFilename):
                            postJsonObject={}
                            with open(postFilename, 'r') as fp:
                                postJsonObject=commentjson.load(fp)
                                # Only authorized viewers get to see likes on posts
                                # Otherwize marketers could gain more social graph info
                                if not authorized:
                                    if postJsonObject.get('likes'):
                                        postJsonObject['likes']={}
                                if 'text/html' in self.headers['Accept']:
                                    self._set_headers('text/html')                    
                                    self.wfile.write(htmlIndividualPost(postJsonObject).encode('utf-8'))
                                else:
                                    self._set_headers('application/json')
                                    self.wfile.write(json.dumps(postJsonObject).encode('utf-8'))
                            self.server.GETbusy=False
                            return
                        else:
                            self._404()
                            self.server.GETbusy=False
                            return
        # get replies to a post /users/nickname/statuses/number/replies
        if self.path.endswith('/replies') or '/replies?page=' in self.path:
            if '/statuses/' in self.path and '/users/' in self.path:
                namedStatus=self.path.split('/users/')[1]
                if '/' in namedStatus:
                    postSections=namedStatus.split('/')
                    if len(postSections)>=4:
                        if postSections[3].startswith('replies'):
                            nickname=postSections[0]
                            statusNumber=postSections[2]
                            if len(statusNumber)>10 and statusNumber.isdigit():
                                #get the replies file
                                boxname='outbox'
                                postDir=self.server.baseDir+'/accounts/'+nickname+'@'+self.server.domain+'/'+boxname
                                postRepliesFilename= \
                                    postDir+'/'+ \
                                    self.server.httpPrefix+':##'+self.server.domainFull+'#users#'+nickname+'#statuses#'+statusNumber+'.replies'
                                if not os.path.isfile(postRepliesFilename):
                                    # There are no replies, so show empty collection
                                    repliesJson = {
                                        '@context': 'https://www.w3.org/ns/activitystreams',
                                        'first': self.server.httpPrefix+'://'+self.server.domainFull+'/users/'+nickname+'/statuses/'+statusNumber+'/replies?page=true',
                                        'id': self.server.httpPrefix+'://'+self.server.domainFull+'/users/'+nickname+'/statuses/'+statusNumber+'/replies',
                                        'last': self.server.httpPrefix+'://'+self.server.domainFull+'/users/'+nickname+'/statuses/'+statusNumber+'/replies?page=true',
                                        'totalItems': 0,
                                        'type': 'OrderedCollection'}
                                    if 'text/html' in self.headers['Accept']:
                                        self._set_headers('text/html')
                                        self.wfile.write(htmlPostReplies(repliesJson).encode('utf-8'))
                                    else:
                                        self._set_headers('application/json')
                                        self.wfile.write(json.dumps(repliesJson).encode('utf-8'))
                                    self.server.GETbusy=False
                                    return
                                else:
                                    # replies exist. Itterate through the text file containing message ids
                                    repliesJson = {
                                        '@context': 'https://www.w3.org/ns/activitystreams',
                                        'id': self.server.httpPrefix+'://'+self.server.domainFull+'/users/'+nickname+'/statuses/'+statusNumber+'?page=true',
                                        'orderedItems': [
                                        ],
                                        'partOf': self.server.httpPrefix+'://'+self.server.domainFull+'/users/'+nickname+'/statuses/'+statusNumber,
                                        'type': 'OrderedCollectionPage'}

                                    # populate the items list with replies
                                    repliesBoxes=['outbox','inbox']
                                    with open(postRepliesFilename,'r') as repliesFile: 
                                        for messageId in repliesFile:
                                            replyFound=False
                                            # examine inbox and outbox
                                            for boxname in repliesBoxes:
                                                searchFilename= \
                                                    self.server.baseDir+ \
                                                    '/accounts/'+nickname+'@'+ \
                                                    self.server.domain+'/'+ \
                                                    boxname+'/'+ \
                                                    messageId.replace('\n','').replace('/','#')+'.json'
                                                if os.path.isfile(searchFilename):
                                                    if authorized or \
                                                       'https://www.w3.org/ns/activitystreams#Public' in open(searchFilename).read():
                                                        with open(searchFilename, 'r') as fp:
                                                            postJsonObject=commentjson.load(fp)
                                                            if postJsonObject['object'].get('cc'):                                                            
                                                                if authorized or \
                                                                   ('https://www.w3.org/ns/activitystreams#Public' in postJsonObject['object']['to'] or \
                                                                    'https://www.w3.org/ns/activitystreams#Public' in postJsonObject['object']['cc']):
                                                                    repliesJson['orderedItems'].append(postJsonObject)
                                                                    replyFound=True
                                                            else:
                                                                if authorized or \
                                                                   'https://www.w3.org/ns/activitystreams#Public' in postJsonObject['object']['to']:
                                                                    repliesJson['orderedItems'].append(postJsonObject)
                                                                    replyFound=True
                                                    break
                                            # if not in either inbox or outbox then examine the shared inbox
                                            if not replyFound:
                                                searchFilename= \
                                                    self.server.baseDir+ \
                                                    '/accounts/inbox@'+ \
                                                    self.server.domain+'/inbox/'+ \
                                                    messageId.replace('\n','').replace('/','#')+'.json'
                                                if os.path.isfile(searchFilename):
                                                    if authorized or \
                                                       'https://www.w3.org/ns/activitystreams#Public' in open(searchFilename).read():
                                                        # get the json of the reply and append it to the collection
                                                        with open(searchFilename, 'r') as fp:
                                                            postJsonObject=commentjson.load(fp)
                                                            if postJsonObject['object'].get('cc'):                                                            
                                                                if authorized or \
                                                                   ('https://www.w3.org/ns/activitystreams#Public' in postJsonObject['object']['to'] or \
                                                                    'https://www.w3.org/ns/activitystreams#Public' in postJsonObject['object']['cc']):
                                                                    repliesJson['orderedItems'].append(postJsonObject)
                                                            else:
                                                                if authorized or \
                                                                   'https://www.w3.org/ns/activitystreams#Public' in postJsonObject['object']['to']:
                                                                    repliesJson['orderedItems'].append(postJsonObject)
                                    # send the replies json
                                    if 'text/html' in self.headers['Accept']:
                                        self._set_headers('text/html')
                                        self.wfile.write(htmlPostReplies(repliesJson).encode('utf-8'))
                                    else:
                                        self._set_headers('application/json')
                                        self.wfile.write(json.dumps(repliesJson).encode('utf-8'))
                                    self.server.GETbusy=False
                                    return

        if self.path.endswith('/roles') and '/users/' in self.path:
            namedStatus=self.path.split('/users/')[1]
            if '/' in namedStatus:
                postSections=namedStatus.split('/')
                nickname=postSections[0]
                actorFilename=self.server.baseDir+'/accounts/'+nickname+'@'+self.server.domain+'.json'
                if os.path.isfile(actorFilename):
                    with open(actorFilename, 'r') as fp:
                        actorJson=commentjson.load(fp)
                        if actorJson.get('roles'):
                            if 'text/html' in self.headers['Accept']:
                                getPerson = \
                                    personLookup(self.server.domain,self.path.replace('/roles',''), \
                                                 self.server.baseDir)
                                if getPerson:
                                    self._set_headers('text/html')
                                    self.wfile.write(htmlProfile(self.server.baseDir, \
                                                                 self.server.httpPrefix, \
                                                                 True, \
                                                                 self.server.ocapAlways, \
                                                                 getPerson,'roles', \
                                                                 self.server.session, \
                                                                 self.server.cachedWebfingers, \
                                                                 self.server.personCache, \
                                                                 actorJson['roles']).encode('utf-8'))     
                            else:
                                self._set_headers('application/json')
                                self.wfile.write(json.dumps(actorJson['roles']).encode('utf-8'))
                            self.server.GETbusy=False
                            return

        if self.path.endswith('/skills') and '/users/' in self.path:
            namedStatus=self.path.split('/users/')[1]
            if '/' in namedStatus:
                postSections=namedStatus.split('/')
                nickname=postSections[0]
                actorFilename=self.server.baseDir+'/accounts/'+nickname+'@'+self.server.domain+'.json'
                if os.path.isfile(actorFilename):
                    with open(actorFilename, 'r') as fp:
                        actorJson=commentjson.load(fp)
                        if actorJson.get('skills'):
                            if 'text/html' in self.headers['Accept']:
                                getPerson = \
                                    personLookup(self.server.domain,self.path.replace('/skills',''), \
                                                 self.server.baseDir)
                                if getPerson:
                                    self._set_headers('text/html')
                                    self.wfile.write(htmlProfile(self.server.baseDir, \
                                                                 self.server.httpPrefix, \
                                                                 True, \
                                                                 self.server.ocapAlways, \
                                                                 getPerson,'skills', \
                                                                 self.server.session, \
                                                                 self.server.cachedWebfingers, \
                                                                 self.server.personCache, \
                                                                 actorJson['skills']).encode('utf-8'))     
                            else:
                                self._set_headers('application/json')
                                self.wfile.write(json.dumps(actorJson['skills']).encode('utf-8'))
                            self.server.GETbusy=False
                            return

        # get an individual post from the path /users/nickname/statuses/number
        if '/statuses/' in self.path and '/users/' in self.path:
            namedStatus=self.path.split('/users/')[1]
            if '/' in namedStatus:
                postSections=namedStatus.split('/')
                if len(postSections)>=3:
                    nickname=postSections[0]
                    statusNumber=postSections[2]
                    if len(statusNumber)>10 and statusNumber.isdigit():
                        postFilename= \
                            self.server.baseDir+'/accounts/'+nickname+'@'+self.server.domain+'/outbox/'+ \
                            self.server.httpPrefix+':##'+self.server.domainFull+'#users#'+nickname+'#statuses#'+statusNumber+'.json'
                        if os.path.isfile(postFilename):
                            postJsonObject={}
                            with open(postFilename, 'r') as fp:
                                postJsonObject=commentjson.load(fp)
                                # Only authorized viewers get to see likes on posts
                                # Otherwize marketers could gain more social graph info
                                if not authorized:
                                    if postJsonObject.get('likes'):
                                        postJsonObject['likes']={}                                    
                                if 'text/html' in self.headers['Accept']:
                                    self._set_headers('text/html')
                                    self.wfile.write(htmlIndividualPost(postJsonObject).encode('utf-8'))
                                else:
                                    self._set_headers('application/json')
                                    self.wfile.write(json.dumps(postJsonObject).encode('utf-8'))
                            self.server.GETbusy=False
                            return
                        else:
                            self._404()
                            self.server.GETbusy=False
                            return
        # get the inbox for a given person
        if self.path.endswith('/inbox'):
            if '/users/' in self.path:
                if authorized:
                    inboxFeed=personBoxJson(self.server.baseDir, \
                                            self.server.domain, \
                                            self.server.port, \
                                            self.path, \
                                            self.server.httpPrefix, \
                                            maxPostsInFeed, 'inbox', \
                                            True,self.server.ocapAlways)
                    if inboxFeed:
                        if 'text/html' in self.headers['Accept']:
                            nickname=self.path.replace('/users/','').replace('/inbox','')
                            if '?page=' in nickname:
                                nickname=nickname.split('?page=')[0]
                            if 'page=' not in self.path:
                                # if no page was specified then show the first
                                inboxFeed=personBoxJson(self.server.baseDir, \
                                                        self.server.domain, \
                                                        self.server.port, \
                                                        self.path+'?page=1', \
                                                        self.server.httpPrefix, \
                                                        maxPostsInFeed, 'inbox', \
                                                        True,self.server.ocapAlways)
                            self._set_headers('text/html')
                            self.wfile.write(htmlInbox(self.server.session, \
                                                       self.server.baseDir, \
                                                       self.server.cachedWebfingers, \
                                                       self.server.personCache, \
                                                       nickname, \
                                                       self.server.domain, \
                                                       inboxFeed).encode('utf-8'))
                        else:
                            self._set_headers('application/json')
                            self.wfile.write(json.dumps(inboxFeed).encode('utf-8'))
                        self.server.GETbusy=False
                        return
                else:
                    if self.server.debug:
                        print('DEBUG: '+nickname+ \
                              ' was not authorized to access '+self.path)
            if self.server.debug:
                print('DEBUG: GET access to inbox is unauthorized')
            self.send_response(405)
            self.end_headers()
            self.server.POSTbusy=False
            return
        
        # get outbox feed for a person
        outboxFeed=personBoxJson(self.server.baseDir,self.server.domain, \
                                 self.server.port,self.path, \
                                 self.server.httpPrefix, \
                                 maxPostsInFeed, 'outbox', \
                                 authorized, \
                                 self.server.ocapAlways)
        if outboxFeed:
            if 'text/html' in self.headers['Accept']:
                nickname=self.path.replace('/users/','').replace('/outbox','')
                if '?page=' in nickname:
                    nickname=nickname.split('?page=')[0]
                if 'page=' not in self.path:
                    # if a page wasn't specified then show the first one
                    outboxFeed=personBoxJson(self.server.baseDir,self.server.domain, \
                                             self.server.port,self.path+'?page=1', \
                                             self.server.httpPrefix, \
                                             maxPostsInFeed, 'outbox', \
                                             authorized, \
                                             self.server.ocapAlways)
                    
                self._set_headers('text/html')
                self.wfile.write(htmlOutbox(self.server.session, \
                                            self.server.baseDir, \
                                            self.server.cachedWebfingers, \
                                            self.server.personCache, \
                                            nickname, \
                                            self.server.domain, \
                                            outboxFeed).encode('utf-8'))
            else:
                self._set_headers('application/json')
                self.wfile.write(json.dumps(outboxFeed).encode('utf-8'))
            self.server.GETbusy=False
            return

        shares=getSharesFeedForPerson(self.server.baseDir, \
                                      self.server.domain, \
                                      self.server.port,self.path, \
                                      self.server.httpPrefix, \
                                      sharesPerPage)
        if shares:
            if 'text/html' in self.headers['Accept']:
                if 'page=' not in self.path:
                    # get a page of shares, not the summary
                    shares=getSharesFeedForPerson(self.server.baseDir,self.server.domain, \
                                                  self.server.port,self.path+'?page=true', \
                                                  self.server.httpPrefix, \
                                                  sharesPerPage)
                getPerson = personLookup(self.server.domain,self.path.replace('/shares',''), \
                                         self.server.baseDir)
                if getPerson:
                    if not self.server.session:
                        if self.server.debug:
                            print('DEBUG: creating new session')
                        self.server.session= \
                            createSession(self.server.domain,self.server.port,self.server.useTor)
                    
                    self._set_headers('text/html')
                    self.wfile.write(htmlProfile(self.server.baseDir, \
                                                 self.server.httpPrefix, \
                                                 authorized, \
                                                 self.server.ocapAlways, \
                                                 getPerson,'shares', \
                                                 self.server.session, \
                                                 self.server.cachedWebfingers, \
                                                 self.server.personCache, \
                                                 shares).encode('utf-8'))                
                    self.server.GETbusy=False
                    return
            else:
                self._set_headers('application/json')
                self.wfile.write(json.dumps(shares).encode('utf-8'))
                self.server.GETbusy=False
                return

        following=getFollowingFeed(self.server.baseDir,self.server.domain, \
                                   self.server.port,self.path, \
                                   self.server.httpPrefix, \
                                   authorized,followsPerPage)
        if following:
            if 'text/html' in self.headers['Accept']:
                if 'page=' not in self.path:
                    # get a page of following, not the summary
                    following=getFollowingFeed(self.server.baseDir,self.server.domain, \
                                               self.server.port,self.path+'?page=true', \
                                               self.server.httpPrefix, \
                                               authorized,followsPerPage)
                getPerson = personLookup(self.server.domain,self.path.replace('/following',''), \
                                         self.server.baseDir)
                if getPerson:
                    if not self.server.session:
                        if self.server.debug:
                            print('DEBUG: creating new session')
                        self.server.session= \
                            createSession(self.server.domain,self.server.port,self.server.useTor)
                    
                    self._set_headers('text/html')
                    self.wfile.write(htmlProfile(self.server.baseDir, \
                                                 self.server.httpPrefix, \
                                                 authorized, \
                                                 self.server.ocapAlways, \
                                                 getPerson,'following', \
                                                 self.server.session, \
                                                 self.server.cachedWebfingers, \
                                                 self.server.personCache, \
                                                 following).encode('utf-8'))                
                    self.server.GETbusy=False
                    return
            else:
                self._set_headers('application/json')
                self.wfile.write(json.dumps(following).encode('utf-8'))
                self.server.GETbusy=False
                return
        followers=getFollowingFeed(self.server.baseDir,self.server.domain, \
                                   self.server.port,self.path, \
                                   self.server.httpPrefix, \
                                   authorized,followsPerPage,'followers')
        if followers:
            if 'text/html' in self.headers['Accept']:
                if 'page=' not in self.path:
                    # get a page of followers, not the summary
                    followers=getFollowingFeed(self.server.baseDir,self.server.domain, \
                                               self.server.port,self.path+'?page=1', \
                                               self.server.httpPrefix, \
                                               authorized,followsPerPage,'followers')
                getPerson = personLookup(self.server.domain,self.path.replace('/followers',''), \
                                         self.server.baseDir)
                if getPerson:
                    if not self.server.session:
                        if self.server.debug:
                            print('DEBUG: creating new session')
                        self.server.session= \
                            createSession(self.server.domain,self.server.port,self.server.useTor)
                    self._set_headers('text/html')
                    self.wfile.write(htmlProfile(self.server.baseDir, \
                                                 self.server.httpPrefix, \
                                                 authorized, \
                                                 self.server.ocapAlways, \
                                                 getPerson,'followers', \
                                                 self.server.session, \
                                                 self.server.cachedWebfingers, \
                                                 self.server.personCache, \
                                                 followers).encode('utf-8'))                
                    self.server.GETbusy=False
                    return
            else:
                self._set_headers('application/json')
                self.wfile.write(json.dumps(followers).encode('utf-8'))
            self.server.GETbusy=False
            return
        # look up a person
        getPerson = personLookup(self.server.domain,self.path, \
                                 self.server.baseDir)
        if getPerson:
            if 'text/html' in self.headers['Accept']:
                if not self.server.session:
                    if self.server.debug:
                        print('DEBUG: creating new session')
                    self.server.session= \
                        createSession(self.server.domain,self.server.port,self.server.useTor)
                self._set_headers('text/html')
                self.wfile.write(htmlProfile(self.server.baseDir, \
                                             self.server.httpPrefix, \
                                             authorized, \
                                             self.server.ocapAlways, \
                                             getPerson,'posts',
                                             self.server.session, \
                                             self.server.cachedWebfingers, \
                                             self.server.personCache).encode('utf-8'))
            else:
                self._set_headers('application/json')
                self.wfile.write(json.dumps(getPerson).encode('utf-8'))
            self.server.GETbusy=False
            return
        # check that a json file was requested
        if not self.path.endswith('.json'):
            if self.server.debug:
                print('DEBUG: GET Not json: '+self.path+' '+self.server.baseDir)
            self._404()
            self.server.GETbusy=False
            return
        # check that the file exists
        filename=self.server.baseDir+self.path
        if os.path.isfile(filename):
            self._set_headers('application/json')
            with open(filename, 'r', encoding='utf-8') as File:
                content = File.read()
                contentJson=json.loads(content)
                self.wfile.write(json.dumps(contentJson).encode('utf-8'))
        else:
            if self.server.debug:
                print('DEBUG: GET Unknown file')
            self._404()
        self.server.GETbusy=False

    def do_HEAD(self):
        self._set_headers('application/json',None)

    def do_POST(self):
        if self.server.debug:
            print('DEBUG: POST to from '+self.server.baseDir+ \
                  ' path: '+self.path+' busy: '+ \
                  str(self.server.POSTbusy))
        if self.server.POSTbusy:
            currTimePOST=int(time.time())
            if currTimePOST-self.server.lastPOST<10:
                self.send_response(429)
                self.end_headers()
                return              
            self.server.lastPOST=currTimePOST

        self.server.POSTbusy=True
        if not self.headers.get('Content-type'):
            print('Content-type header missing')
            self.send_response(400)
            self.end_headers()
            self.server.POSTbusy=False
            return

        # remove any trailing slashes from the path
        self.path=self.path.replace('/outbox/','/outbox').replace('/inbox/','/inbox').replace('/shares/','/shares').replace('/sharedInbox/','/sharedInbox')

        # if this is a POST to teh outbox then check authentication
        self.outboxAuthenticated=False
        self.postToNickname=None

        if self.path.startswith('/login'):
            # get the contents of POST containing login credentials
            length = int(self.headers['Content-length'])
            if length>512:
                print('Login failed - credentials too long')
                self.send_response(401)
                self.end_headers()
                self.server.POSTbusy=False
                return                
            loginParams=self.rfile.read(length).decode('utf-8')            
            loginNickname,loginPassword=htmlGetLoginCredentials(loginParams,self.server.lastLoginTime)
            if loginNickname:
                self.server.lastLoginTime=int(time.time())
                authHeader=createBasicAuthHeader(loginNickname,loginPassword)
                if not authorizeBasic(self.server.baseDir,'/users/'+loginNickname+'/outbox',authHeader,False):
                    print('Login failed: '+loginNickname)
                    # remove any token
                    if self.server.tokens.get(loginNickname):
                        del self.server.tokensLookup[self.server.tokens[loginNickname]]
                        del self.server.tokens[loginNickname]
                        del self.server.salts[loginNickname]
                    self.send_response(303)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.send_header('Set-Cookie', 'epicyon=; SameSite=Strict')
                    self.send_header('Location', '/login')
                    self.end_headers()                    
                    self.server.POSTbusy=False
                    return
                else:
                    # login success - redirect with authorization
                    print('Login success: '+loginNickname)
                    self.send_response(303)
                    # This produces a deterministic token based on nick+password+salt
                    # But notice that the salt is ephemeral, so a server reboot changes them.
                    # This allows you to be logged in on two or more devices with the
                    # same token, but also ensures that if an adversary obtains the token
                    # then rebooting the server is sufficient to thwart them, without
                    # any password changes.
                    if not self.server.salts.get(loginNickname):
                        self.server.salts[loginNickname]=createPassword(32)
                    self.server.tokens[loginNickname]=sha256((loginNickname+loginPassword+self.server.salts[loginNickname]).encode('utf-8')).hexdigest()
                    self.server.tokensLookup[self.server.tokens[loginNickname]]=loginNickname
                    self.send_header('Set-Cookie', 'epicyon='+self.server.tokens[loginNickname]+'; SameSite=Strict')
                    self.send_header('Location', '/users/'+loginNickname+'/inbox')
                    self.end_headers()
                    self.server.POSTbusy=False
                    return
            self.send_response(200)
            self.end_headers()
            self.server.POSTbusy=False
            return

        if self.path.endswith('/outbox') or self.path.endswith('/shares'):
            if '/users/' in self.path:
                if self._isAuthorized():
                    self.outboxAuthenticated=True
                    pathUsersSection=self.path.split('/users/')[1]
                    self.postToNickname=pathUsersSection.split('/')[0]
            if not self.outboxAuthenticated:
                self.send_response(405)
                self.end_headers()
                self.server.POSTbusy=False
                return

        # check that the post is to an expected path
        if not (self.path.endswith('/outbox') or \
                self.path.endswith('/inbox') or \
                self.path.endswith('/shares') or \
                self.path.endswith('/caps/new') or \
                self.path=='/sharedInbox'):
            print('Attempt to POST to invalid path '+self.path)
            self.send_response(400)
            self.end_headers()
            self.server.POSTbusy=False
            return

        # read the message and convert it into a python dictionary
        length = int(self.headers['Content-length'])
        if self.server.debug:
            print('DEBUG: content-length: '+str(length))
        if not self.headers['Content-type'].startswith('image/'):
            if length>self.server.maxMessageLength:
                print('Maximum message length exceeded '+str(length))
                self.send_response(400)
                self.end_headers()
                self.server.POSTbusy=False
                return
        else:
            if length>self.server.maxImageSize:
                print('Maximum image size exceeded '+str(length))
                self.send_response(400)
                self.end_headers()
                self.server.POSTbusy=False
                return

        # receive images to the outbox
        if self.headers['Content-type'].startswith('image/') and \
           '/users/' in self.path:
            if not self.outboxAuthenticated:
                if self.server.debug:
                    print('DEBUG: unathenticated attempt to post image to outbox')
                self.send_response(403)
                self.end_headers()
                self.server.POSTbusy=False
                return            
            pathUsersSection=self.path.split('/users/')[1]
            if '/' not in pathUsersSection:
                self.send_response(404)
                self.end_headers()
                self.server.POSTbusy=False
                return                
            self.postFromNickname=pathUsersSection.split('/')[0]
            accountsDir=self.server.baseDir+'/accounts/'+self.postFromNickname+'@'+self.server.domain
            if not os.path.isdir(accountsDir):
                self.send_response(404)
                self.end_headers()
                self.server.POSTbusy=False
                return                
            mediaBytes=self.rfile.read(length)
            mediaFilenameBase=accountsDir+'/upload'
            mediaFilename=mediaFilenameBase+'.png'
            if self.headers['Content-type'].endswith('jpeg'):
                mediaFilename=mediaFilenameBase+'.jpg'
            if self.headers['Content-type'].endswith('gif'):
                mediaFilename=mediaFilenameBase+'.gif'
            with open(mediaFilename, 'wb') as avFile:
                avFile.write(mediaBytes)
            if self.server.debug:
                print('DEBUG: image saved to '+mediaFilename)
            self.send_response(201)
            self.end_headers()
            self.server.POSTbusy=False
            return            

        # refuse to receive non-json content
        if self.headers['Content-type'] != 'application/json':
            print("POST is not json: "+self.headers['Content-type'])
            self.send_response(400)
            self.end_headers()
            self.server.POSTbusy=False
            return

        if self.server.debug:
            print('DEBUG: Reading message')

        messageBytes=self.rfile.read(length)
        messageJson=json.loads(messageBytes)
            
        # https://www.w3.org/TR/activitypub/#object-without-create
        if self.outboxAuthenticated:
            if self._postToOutbox(messageJson):                
                if messageJson.get('id'):
                    self.headers['Location']= \
                        messageJson['id'].replace('/activity','')
                self.send_response(201)
                self.end_headers()
                self.server.POSTbusy=False
                return
            else:
                self.send_response(403)
                self.end_headers()
                self.server.POSTbusy=False
                return

        # check the necessary properties are available
        if self.server.debug:
            print('DEBUG: Check message has params')

        if self.path.endswith('/inbox') or \
           self.path=='/sharedInbox':
            if not inboxMessageHasParams(messageJson):
                if self.server.debug:
                    pprint(messageJson)
                    print("DEBUG: inbox message doesn't have the required parameters")
                self.send_response(403)
                self.end_headers()
                self.server.POSTbusy=False
                return

        if not inboxPermittedMessage(self.server.domain, \
                                     messageJson, \
                                     self.server.federationList):
            if self.server.debug:
                # https://www.youtube.com/watch?v=K3PrSj9XEu4
                print('DEBUG: Ah Ah Ah')
            self.send_response(403)
            self.end_headers()
            self.server.POSTbusy=False
            return

        if self.server.debug:
            pprint(messageJson)

        if not self.headers.get('signature'):
            if 'keyId=' not in self.headers['signature']:
                if self.server.debug:
                    print('DEBUG: POST to inbox has no keyId in header signature parameter')
                    self.send_response(403)
                    self.end_headers()
                    self.server.POSTbusy=False
                    return
        
        if self.server.debug:
            print('DEBUG: POST saving to inbox queue')
        if '/users/' in self.path:
            pathUsersSection=self.path.split('/users/')[1]
            if '/' not in pathUsersSection:
                if self.server.debug:
                    print('DEBUG: This is not a users endpoint')
            else:
                self.postToNickname=pathUsersSection.split('/')[0]
                if self.postToNickname:
                    queueStatus=self._updateInboxQueue(self.postToNickname,messageJson)
                    if queueStatus==0:
                        self.send_response(200)
                        self.end_headers()
                        self.server.POSTbusy=False
                        return
                    if queueStatus==1:
                        self.send_response(503)
                        self.end_headers()
                        self.server.POSTbusy=False
                        return                    
            self.send_response(403)
            self.end_headers()
            self.server.POSTbusy=False
            return
        else:
            if self.path == '/sharedInbox' or self.path == '/inbox':
                print('DEBUG: POST to shared inbox')
                queueStatus-_updateInboxQueue('inbox',messageJson)
                if queueStatus==0:
                    self.send_response(200)
                    self.end_headers()
                    self.server.POSTbusy=False
                    return
                if queueStatus==1:
                    self.send_response(503)
                    self.end_headers()
                    self.server.POSTbusy=False
                    return                    
        self.send_response(200)
        self.end_headers()
        self.server.POSTbusy=False

def runDaemon(clientToServer: bool,baseDir: str,domain: str, \
              port=80,httpPrefix='https', \
              fedList=[],noreply=False,nolike=False,nopics=False, \
              noannounce=False,cw=False,ocapAlways=False, \
              useTor=False,maxReplies=64, \
              domainMaxPostsPerDay=8640,accountMaxPostsPerDay=8640, \
              allowDeletion=False,debug=False) -> None:
    if len(domain)==0:
        domain='localhost'
    if '.' not in domain:
        if domain != 'localhost':
            print('Invalid domain: ' + domain)
            return

    serverAddress = ('', port)
    httpd = ThreadingHTTPServer(serverAddress, PubServer)
    httpd.domain=domain
    httpd.port=port
    httpd.domainFull=domain
    if port!=80 and port!=443:
        httpd.domainFull=domain+':'+str(port)
    httpd.httpPrefix=httpPrefix
    httpd.debug=debug
    httpd.federationList=fedList.copy()
    httpd.baseDir=baseDir
    httpd.personCache={}
    httpd.cachedWebfingers={}
    httpd.useTor=useTor
    httpd.session = None
    httpd.sessionLastUpdate=0
    httpd.lastGET=0
    httpd.lastPOST=0
    httpd.GETbusy=False
    httpd.POSTbusy=False
    httpd.receivedMessage=False
    httpd.inboxQueue=[]
    httpd.sendThreads=[]
    httpd.postLog=[]
    httpd.maxQueueLength=16
    httpd.ocapAlways=ocapAlways
    httpd.maxMessageLength=5000
    httpd.maxImageSize=10*1024*1024
    httpd.allowDeletion=allowDeletion
    httpd.lastLoginTime=0
    httpd.salts={}
    httpd.tokens={}
    httpd.tokensLookup={}
    httpd.acceptedCaps=["inbox:write","objects:read"]
    if noreply:
        httpd.acceptedCaps.append('inbox:noreply')
    if nolike:
        httpd.acceptedCaps.append('inbox:nolike')
    if nopics:
        httpd.acceptedCaps.append('inbox:nopics')
    if noannounce:
        httpd.acceptedCaps.append('inbox:noannounce')
    if cw:
        httpd.acceptedCaps.append('inbox:cw')

    if not os.path.isdir(baseDir+'/accounts/inbox@'+domain):
        print('Creating shared inbox: inbox@'+domain)
        createSharedInbox(baseDir,'inbox',domain,port,httpPrefix)

    print('Creating inbox queue')
    httpd.thrInboxQueue= \
        threadWithTrace(target=runInboxQueue, \
                        args=(baseDir,httpPrefix,httpd.sendThreads, \
                              httpd.postLog,httpd.cachedWebfingers, \
                              httpd.personCache,httpd.inboxQueue, \
                              domain,port,useTor,httpd.federationList, \
                              httpd.ocapAlways,maxReplies, \
                              domainMaxPostsPerDay,accountMaxPostsPerDay, \
                              allowDeletion,debug,httpd.acceptedCaps),daemon=True)
    httpd.thrInboxQueue.start()
    if clientToServer:
        print('Running ActivityPub client on ' + domain + ' port ' + str(port))
    else:
        print('Running ActivityPub server on ' + domain + ' port ' + str(port))
    httpd.serve_forever()
