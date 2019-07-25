__filename__ = "webinterface.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "0.0.1"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

import json
import time
import os
from shutil import copyfile
from pprint import pprint
from person import personBoxJson
from utils import getNicknameFromActor
from utils import getDomainFromActor
from posts import getPersonBox

def htmlGetLoginCredentials(loginParams: str,lastLoginTime: int) -> (str,str):
    """Receives login credentials via HTTPServer POST
    """
    if not loginParams.startswith('username='):
        return None,None
    # minimum time between login attempts
    currTime=int(time.time())
    if currTime<lastLoginTime+5:
        return None,None
    if '&' not in loginParams:
        return None,None
    loginArgs=loginParams.split('&')
    nickname=None
    password=None
    for arg in loginArgs:
        if '=' in arg:
            if arg.split('=',1)[0]=='username':
                nickname=arg.split('=',1)[1]
            elif arg.split('=',1)[0]=='password':
                password=arg.split('=',1)[1]
    return nickname,password

def htmlLogin(baseDir: str) -> str:
    if not os.path.isfile(baseDir+'/accounts/login.png'):
        copyfile(baseDir+'/img/login.png',baseDir+'/accounts/login.png')
    # /login?nickname=[username]&password=[password]&remember=on
    loginCSS= \
        'body, html {' \
        '    height: 100%;' \
        '    font-family: Arial, Helvetica, sans-serif;' \
        '    max-width: 60%;' \
        '    min-width: 600px;' \
        '    margin: 0 auto;' \
        '}' \
        '' \
        'form {' \
        '  border: 3px solid #f1f1f1;' \
        '}' \
        '' \
        'input[type=text], input[type=password] {' \
        '  width: 100%;' \
        '  padding: 12px 20px;' \
        '  margin: 8px 0;' \
        '  display: inline-block;' \
        '  border: 1px solid #ccc;' \
        '  box-sizing: border-box;' \
        '}' \
        '' \
        'button {' \
        '  background-color: #999;' \
        '  color: white;' \
        '  padding: 14px 20px;' \
        '  margin: 8px 0;' \
        '  border: none;' \
        '  cursor: pointer;' \
        '  width: 100%;' \
        '  font-size: 24px;' \
        '}' \
        '' \
        'button:hover {' \
        '  opacity: 0.8;' \
        '}' \
        '' \
        '.imgcontainer {' \
        '  text-align: center;' \
        '  margin: 24px 0 12px 0;' \
        '}' \
        '' \
        'img.avatar {' \
        '  width: 40%;' \
        '  border-radius: 50%;' \
        '}' \
        '' \
        '.container {' \
        '  padding: 16px;' \
        '}' \
        '' \
        'span.psw {' \
        '  float: right;' \
        '  padding-top: 16px;' \
        '}' \
        '' \
        '@media screen and (max-width: 300px) {' \
        '  span.psw {' \
        '    display: block;' \
        '    float: none;' \
        '  }' \
        '  .cancelbtn {' \
        '    width: 100%;' \
        '  }' \
        '}'
    
    loginForm=htmlHeader(loginCSS)
    loginForm+= \
        ' <form method="POST" action="/login">' \
        '  <div class="imgcontainer">' \
        '    <img src="login.png" alt="login image" class="loginimage">' \
        '  </div>' \
        '' \
        '  <div class="container">' \
        '    <label for="nickname"><b>Nickname</b></label>' \
        '    <input type="text" placeholder="Enter Nickname" name="username" required>' \
        '' \
        '    <label for="password"><b>Password</b></label>' \
        '    <input type="password" placeholder="Enter Password" name="password" required>' \
        '' \
        '    <button type="submit" name="submit">Login</button>' \
        '  </div>' \
        '</form>'
    loginForm+=htmlFooter()
    return loginForm

def htmlHeader(css=None,lang='en') -> str:
    if not css:        
        htmlStr= \
            '<!DOCTYPE html>\n' \
            '<html lang="'+lang+'">\n' \
            '  <meta charset="utf-8">\n' \
            '  <style>\n' \
            '    @import url("epicyon-profile.css");\n'+ \
            '  </style>\n' \
            '  <body>\n'
    else:
        htmlStr= \
            '<!DOCTYPE html>\n' \
            '<html lang="'+lang+'">\n' \
            '  <meta charset="utf-8">\n' \
            '  <style>\n'+css+'</style>\n' \
            '  <body>\n'        
    return htmlStr

def htmlFooter() -> str:
    htmlStr= \
        '  </body>\n' \
        '</html>\n'
    return htmlStr

def htmlProfilePosts(baseDir: str,httpPrefix: str, \
                     authorized: bool,ocapAlways: bool, \
                     nickname: str,domain: str,port: int, \
                     session,wfRequest: {},personCache: {}) -> str:
    """Shows posts on the profile screen
    """
    profileStr=''
    outboxFeed= \
        personBoxJson(baseDir,domain, \
                      port,'/users/'+nickname+'/outbox?page=1', \
                      httpPrefix, \
                      4, 'outbox', \
                      authorized, \
                      ocapAlways)
    for item in outboxFeed['orderedItems']:
        if item['type']=='Create':
            profileStr+= \
                individualPostAsHtml(session,wfRequest,personCache, \
                                     domain,item)
    return profileStr

def htmlProfileFollowing(baseDir: str,httpPrefix: str, \
                         authorized: bool,ocapAlways: bool, \
                         nickname: str,domain: str,port: int, \
                         session,wfRequest: {},personCache: {}, \
                         followingJson: {}) -> str:
    """Shows following on the profile screen
    """
    profileStr=''
    for item in followingJson['orderedItems']:
        profileStr+=individualFollowAsHtml(session,wfRequest,personCache,domain,item)
    return profileStr

def htmlProfileRoles(nickname: str,domain: str,rolesJson: {}) -> str:
    """Shows roles on the profile screen
    """
    profileStr=''
    for project,rolesList in rolesJson.items():
        profileStr+='<div class="roles"><h2>'+project+'</h2><div class="roles-inner">'
        for role in rolesList:
            profileStr+='<h3>'+role+'</h3>'
        profileStr+='</div></div>'
    if len(profileStr)==0:
        profileStr+='<p>@'+nickname+'@'+domain+' has no roles assigned</p>'
    else:
        profileStr='<div>'+profileStr+'</div>'
    return profileStr

def htmlProfileSkills(nickname: str,domain: str,skillsJson: {}) -> str:
    """Shows skills on the profile screen
    """
    profileStr=''
    for skill,level in skillsJson.items():
        profileStr+='<div>'+skill+'<br><div id="myProgress"><div id="myBar" style="width:'+str(level)+'%"></div></div></div><br>'
    if len(profileStr)==0:
        profileStr+='<p>@'+nickname+'@'+domain+' has no skills assigned</p>'
    else:
        profileStr='<center><div class="skill-title">'+profileStr+'</div></center>'
    return profileStr

def htmlProfileShares(nickname: str,domain: str,sharesJson: {}) -> str:
    """Shows shares on the profile screen
    """
    profileStr=''
    for item in sharesJson['orderedItems']:
        profileStr+='<div class="container">'
        profileStr+='<p class="share-title">'+item['displayName']+'</p>'
        profileStr+='<a href="'+item['imageUrl']+'">'
        profileStr+='<img src="'+item['imageUrl']+'" alt="Item image"></a>'
        profileStr+='<p>'+item['summary']+'</p>'
        profileStr+='<p><b>Type:</b> '+item['itemType']+' '
        profileStr+='<b>Category:</b> '+item['category']+' '
        profileStr+='<b>Location:</b> '+item['location']+'</p>'
        profileStr+='</div>'
    if len(profileStr)==0:
        profileStr+='<p>@'+nickname+'@'+domain+' is not sharing any items</p>'
    else:
        profileStr='<div class="share-title">'+profileStr+'</div>'
    return profileStr

def htmlProfile(baseDir: str,httpPrefix: str,authorized: bool, \
                ocapAlways: bool,profileJson: {},selected: str, \
                session,wfRequest: {},personCache: {}, \
                extraJson=None) -> str:
    """Show the profile page as html
    """
    nickname=profileJson['name']
    if not nickname:
        return ""
    preferredName=profileJson['preferredUsername']
    domain,port=getDomainFromActor(profileJson['id'])
    if not domain:
        return ""
    domainFull=domain
    if port:
        domainFull=domain+':'+str(port)
    profileDescription=profileJson['publicKey']['summary']
    profileDescription='A test description'
    postsButton='button'
    followingButton='button'
    followersButton='button'
    rolesButton='button'
    skillsButton='button'
    sharesButton='button'
    if selected=='posts':
        postsButton='buttonselected'
    elif selected=='following':
        followingButton='buttonselected'
    elif selected=='followers':
        followersButton='buttonselected'
    elif selected=='roles':
        rolesButton='buttonselected'
    elif selected=='skills':
        skillsButton='buttonselected'
    elif selected=='shares':
        sharesButton='buttonselected'
    actor=profileJson['id']
    profileStr= \
        ' <div class="hero-image">' \
        '  <div class="hero-text">' \
        '    <img src="'+profileJson['icon']['url']+'" alt="'+nickname+'@'+domainFull+'">' \
        '    <h1>'+preferredName+'</h1>' \
        '    <p><b>@'+nickname+'@'+domainFull+'</b></p>' \
        '    <p>'+profileDescription+'</p>' \
        '  </div>' \
        '</div>' \
        '<div class="container">\n' \
        '  <center>' \
        '    <a href="'+actor+'"><button class="'+postsButton+'"><span>Posts </span></button></a>' \
        '    <a href="'+actor+'/following"><button class="'+followingButton+'"><span>Following </span></button></a>' \
        '    <a href="'+actor+'/followers"><button class="'+followersButton+'"><span>Followers </span></button></a>' \
        '    <a href="'+actor+'/roles"><button class="'+rolesButton+'"><span>Roles </span></button></a>' \
        '    <a href="'+actor+'/skills"><button class="'+skillsButton+'"><span>Skills </span></button></a>' \
        '    <a href="'+actor+'/shares"><button class="'+sharesButton+'"><span>Shares </span></button></a>' \
        '  </center>' \
        '</div>'

    with open(baseDir+'/epicyon-profile.css', 'r') as cssFile:
        profileStyle = cssFile.read().replace('image.png',actor+'/image.png')

        if selected=='posts':
            profileStr+= \
                htmlProfilePosts(baseDir,httpPrefix,authorized, \
                                 ocapAlways,nickname,domain,port, \
                                 session,wfRequest,personCache)
        if selected=='following' or selected=='followers':
            profileStr+= \
                htmlProfileFollowing(baseDir,httpPrefix, \
                                     authorized,ocapAlways,nickname, \
                                     domain,port,session, \
                                     wfRequest,personCache,extraJson)
        if selected=='roles':
            profileStr+= \
                htmlProfileRoles(nickname,domainFull,extraJson)
        if selected=='skills':
            profileStr+= \
                htmlProfileSkills(nickname,domainFull,extraJson)
        if selected=='shares':
            profileStr+= \
                htmlProfileShares(nickname,domainFull,extraJson)
        profileStr=htmlHeader(profileStyle)+profileStr+htmlFooter()
    return profileStr

def individualFollowAsHtml(session,wfRequest: {}, \
                           personCache: {},domain: str, \
                           followUrl: str) -> str:
    nickname=getNicknameFromActor(followUrl)
    domain,port=getDomainFromActor(followUrl)
    titleStr='@'+nickname+'@'+domain
    avatarUrl=followUrl+'/avatar.png'
    if domain not in followUrl:
        inboxUrl,pubKeyId,pubKey,fromPersonId,sharedInbox,capabilityAcquisition,avatarUrl2,preferredName = \
            getPersonBox(session,wfRequest,personCache,'outbox')
        if avatarUrl2:
            avatarUrl=avatarUrl2
        if preferredName:
            titleStr=preferredName+' '+titleStr
    return \
        '<div class="container">\n' \
        '<a href="'+followUrl+'">' \
        '<img src="'+avatarUrl+'" alt="Avatar">\n'+ \
        '<p>'+titleStr+'</p></a>'+ \
        '</div>\n'

def individualPostAsHtml(session,wfRequest: {},personCache: {}, \
                         domain: str,postJsonObject: {}) -> str:
    avatarPosition=''
    containerClass='container'
    timeClass='time-right'
    nickname=getNicknameFromActor(postJsonObject['actor'])
    domain,port=getDomainFromActor(postJsonObject['actor'])
    titleStr='@'+nickname+'@'+domain
    if postJsonObject['object']['inReplyTo']:
        containerClass='container darker'
        avatarPosition=' class="right"'
        timeClass='time-left'
        if '/statuses/' in postJsonObject['object']['inReplyTo']:
            replyNickname=getNicknameFromActor(postJsonObject['object']['inReplyTo'])
            replyDomain,replyPort=getDomainFromActor(postJsonObject['object']['inReplyTo'])
            if replyNickname and replyDomain:
                titleStr+=' <i>replying to</i> <a href="'+postJsonObject['object']['inReplyTo']+'">@'+replyNickname+'@'+replyDomain+'</a>'
        else:
            titleStr+=' <i>replying to</i> '+postJsonObject['object']['inReplyTo']
    attachmentStr=''
    if postJsonObject['object']['attachment']:
        if isinstance(postJsonObject['object']['attachment'], list):
            attachmentCtr=0
            for attach in postJsonObject['object']['attachment']:
                if attach.get('mediaType') and attach.get('url'):
                    mediaType=attach['mediaType']
                    imageDescription=''
                    if attach.get('name'):
                        imageDescription=attach['name']
                    if mediaType=='image/png' or \
                       mediaType=='image/jpeg' or \
                       mediaType=='image/gif':
                        if attach['url'].endswith('.png') or \
                           attach['url'].endswith('.jpg') or \
                           attach['url'].endswith('.jpeg') or \
                           attach['url'].endswith('.gif'):
                            if attachmentCtr>0:
                                attachmentStr+='<br>'
                            attachmentStr+= \
                                '<a href="'+attach['url']+'">' \
                                '<img src="'+attach['url']+'" alt="'+imageDescription+'" title="'+imageDescription+'" class="attachment"></a>\n'
                            attachmentCtr+=1

    avatarUrl=postJsonObject['actor']+'/avatar.png'
    if domain not in postJsonObject['actor']:
        inboxUrl,pubKeyId,pubKey,fromPersonId,sharedInbox,capabilityAcquisition,avatarUrl2,preferredName = \
            getPersonBox(session,wfRequest,personCache,'outbox')
        if avatarUrl2:
            avatarUrl=avatarUrl2
        if preferredName:
            titleStr=preferredName+' '+titleStr

    return \
        '<div class="'+containerClass+'">\n' \
        '<a href="'+postJsonObject['actor']+'">' \
        '<img src="'+avatarUrl+'" alt="Avatar"'+avatarPosition+'></a>\n'+ \
        '<p class="post-title">'+titleStr+'</p>'+ \
        postJsonObject['object']['content']+'\n'+ \
        attachmentStr+ \
        '<span class="'+timeClass+'">'+postJsonObject['object']['published']+'</span>\n'+ \
        '</div>\n'

def htmlTimeline(session,baseDir: str,wfRequest: {},personCache: {}, \
                 nickname: str,domain: str,timelineJson: {},boxName: str) -> str:
    """Show the timeline as html
    """
    with open(baseDir+'/epicyon-profile.css', 'r') as cssFile:
        profileStyle = \
            cssFile.read().replace('banner.png', \
                                   '/users/'+nickname+'/banner.png')

    localButton='button'
    personalButton='button'
    federatedButton='button'
    if boxName=='inbox':
        localButton='buttonselected'
    elif boxName=='outbox':
        personalButton='buttonselected'
    elif boxName=='federated':
        federatedButton='buttonselected'

    actor='/users/'+nickname
    tlStr=htmlHeader(profileStyle)
    tlStr+= \
        '<div class="timeline-banner">' \
        '</div>' \
        '<div class="container">\n' \
        '  <center>' \
        '    <a href="'+actor+'/inbox"><button class="'+localButton+'"><span>Local </span></button></a>' \
        '    <a href="'+actor+'/outbox"><button class="'+personalButton+'"><span>Personal </span></button></a>' \
        '    <a href="'+actor+'/federated"><button class="'+federatedButton+'"><span>Federated </span></button></a>' \
        '  </center>' \
        '</div>'
    for item in timelineJson['orderedItems']:
        if item['type']=='Create':
            tlStr+=individualPostAsHtml(session,wfRequest,personCache, \
                                        domain,item)
    tlStr+=htmlFooter()
    return tlStr

def htmlInbox(session,baseDir: str,wfRequest: {},personCache: {}, \
              nickname: str,domain: str,inboxJson: {}) -> str:
    """Show the inbox as html
    """
    return htmlTimeline(session,baseDir,wfRequest,personCache, \
                        nickname,domain,inboxJson,'inbox')

def htmlOutbox(session,baseDir: str,wfRequest: {},personCache: {}, \
               nickname: str,domain: str,outboxJson: {}) -> str:
    """Show the Outbox as html
    """
    return htmlTimeline(session,baseDir,wfRequest,personCache, \
                        nickname,domain,outboxJson,'outbox')

def htmlIndividualPost(session,wfRequest: {},personCache: {}, \
                       domain: str,postJsonObject: {}) -> str:
    """Show an individual post as html
    """
    return htmlHeader()+ \
        individualPostAsHtml(session,wfRequest,personCache, \
                             domain,postJsonObject)+ \
        htmlFooter()

def htmlPostReplies(postJsonObject: {}) -> str:
    """Show the replies to an individual post as html
    """
    return htmlHeader()+"<h1>Replies</h1>"+htmlFooter()
