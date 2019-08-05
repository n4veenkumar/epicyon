__filename__ = "content.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "0.0.1"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

import os
import commentjson

def addMentions(baseDir: str,httpPrefix: str, \
                nickname: str,domain: str,content: str, \
                recipients: []) -> str:
    """ Replaces plaintext mentions such as @nick@domain into html
    by matching against known following accounts
    """
    if content.startswith('<p>'):
        return content
    wordsOnly=content.replace(',',' ').replace(';',' ').replace('.',' ').replace(':',' ')
    words=wordsOnly.split(' ')
    replaceMentions={}
    if ':' in domain:
        domain=domain.split(':')[0]
    followingFilename=baseDir+'/accounts/'+nickname+'@'+domain+'/following.txt'
    if not os.path.isfile(followingFilename):
        content=content.replace('\n','</p><p>')
        content='<p>'+content+'</p>'
        return content.replace('<p></p>','')
    with open(followingFilename, "r") as f:
        following = f.readlines()
    for wordStr in words:
        if wordStr.startswith('@'):
            if len(wordStr)>1:
                possibleHandle=wordStr[1:]
                if '@' in possibleHandle:
                    possibleNickname=possibleHandle.split('@')[0]
                    possibleDomain=possibleHandle.split('@')[1]
                    replaceFound=False
                    for follow in following:
                        if follow.replace('\n','')==possibleHandle:
                            recipientActor=httpPrefix+"://"+possibleDomain+"/users/"+possibleNickname
                            if recipientActor not in recipients:
                                recipients.append(recipientActor)
                            replaceMentions[wordStr]="<span class=\"h-card\"><a href=\""+httpPrefix+"://"+possibleDomain+"/@"+possibleNickname+"\" class=\"u-url mention\">@<span>"+possibleNickname+"</span></a></span>"
                            replaceFound=True
                            break
                    if not replaceFound:
                        # fall back to a best effort match if an exact one is not found
                        for follow in following:
                            if follow.startswith(possibleNickname+'@'):
                                replaceDomain=follow.replace('\n','').split('@')[1]
                                recipientActor=httpPrefix+"://"+replaceDomain+"/users/"+possibleNickname
                                if recipientActor not in recipients:
                                    recipients.append(recipientActor)
                                replaceMentions[wordStr]="<span class=\"h-card\"><a href=\""+httpPrefix+"://"+replaceDomain+"/@"+possibleNickname+"\" class=\"u-url mention\">@<span>"+possibleNickname+"</span></a></span>"
                                replaceFound=True
                                break
    # do the mention replacements
    for wordStr,replaceStr in replaceMentions.items():
        content=content.replace(wordStr,replaceStr)
    content=content.replace('\n','</p><p>')
    return '<p>'+content+'</p>'
                
def getMentionsFromHtml(htmlText: str,matchStr="<span class=\"h-card\"><a href=\"") -> []:
    """Extracts mentioned actors from the given html content string
    """
    mentions=[]
    if matchStr not in htmlText:
        return mentions
    mentionsList=htmlText.split(matchStr)
    for mentionStr in mentionsList:
        if '"' not in mentionStr:
            continue
        actorStr=mentionStr.split('"')[0]
        if actorStr.startswith('http') or \
           actorStr.startswith('dat:'):
            mentions.append(actorStr)
    return mentions
