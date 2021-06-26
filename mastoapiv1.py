__filename__ = "mastoapiv1.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "1.2.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"
__module_group__ = "API"

import os
from utils import loadJson
from utils import getConfigParam
from metadata import metaDataInstance


def _getMastApiV1Id(path: str) -> int:
    """Extracts the mastodon Id number from the given path
    """
    mastoId = None
    idPath = '/api/v1/accounts/:'
    if not path.startswith(idPath):
        return None
    mastoIdStr = path.replace(idPath, '')
    if '/' in mastoIdStr:
        mastoIdStr = mastoIdStr.split('/')[0]
    if mastoIdStr.isdigit():
        mastoId = int(mastoIdStr)
        return mastoId
    return None


def getMastoApiV1IdFromNickname(nickname: str) -> int:
    """Given an account nickname return the corresponding mastodon id
    """
    return int.from_bytes(nickname.encode('utf-8'), 'little')


def _intToBytes(num: int) -> str:
    if num == 0:
        return b""
    else:
        return _intToBytes(num // 256) + bytes([num % 256])


def getNicknameFromMastoApiV1Id(mastoId: int) -> str:
    """Given the mastodon Id return the nickname
    """
    nickname = _intToBytes(mastoId).decode()
    return nickname[::-1]


def _getMastoApiV1Account(baseDir: str, nickname: str, domain: str) -> {}:
    """See https://github.com/McKael/mastodon-documentation/
    blob/master/Using-the-API/API.md#account
    Authorization has already been performed
    """
    accountFilename = \
        baseDir + '/accounts/' + nickname + '@' + domain + '.json'
    if not os.path.isfile(accountFilename):
        return {}
    accountJson = loadJson(accountFilename)
    if not accountJson:
        return {}
    mastoAccountJson = {
        "id": getMastoApiV1IdFromNickname(nickname),
        "username": nickname,
        "acct": nickname,
        "display_name": accountJson['name'],
        "locked": accountJson['manuallyApprovesFollowers'],
        "created_at": "2016-10-05T10:30:00Z",
        "followers_count": 0,
        "following_count": 0,
        "statuses_count": 0,
        "note": accountJson['summary'],
        "url": accountJson['id'],
        "avatar": accountJson['icon']['url'],
        "avatar_static": accountJson['icon']['url'],
        "header": accountJson['image']['url'],
        "header_static": accountJson['image']['url']
    }
    return mastoAccountJson


def mastoApiV1Response(path: str, callingDomain: str,
                       authorized: bool,
                       httpPrefix: str,
                       baseDir: str, nickname: str, domain: str,
                       domainFull: str,
                       onionDomain: str, i2pDomain: str,
                       translate: {},
                       registration: bool,
                       systemLanguage: str,
                       projectVersion: str,
                       customEmoji: [],
                       showNodeInfoAccounts: bool,
                       brochMode: bool) -> ({}, str):
    """This is a vestigil mastodon API for the purpose
       of returning an empty result to sites like
       https://mastopeek.app-dist.eu
    """
    sendJson = None
    sendJsonStr = ''

    # parts of the api needing authorization
    if authorized and nickname:
        if path == '/api/v1/accounts/verify_credentials':
            sendJson = _getMastoApiV1Account(baseDir, nickname, domain)
            sendJsonStr = 'masto API account sent for ' + nickname

    # Parts of the api which don't need authorization
    mastoId = _getMastApiV1Id(path)
    if mastoId is not None:
        pathNickname = getNicknameFromMastoApiV1Id(mastoId)
        if pathNickname:
            originalPath = path
            if '/followers?' in path or \
               '/following?' in path or \
               '/search?' in path or \
               '/relationships?' in path or \
               '/statuses?' in path:
                path = path.split('?')[0]
            if path.endswith('/followers'):
                sendJson = []
                sendJsonStr = 'masto API followers sent for ' + nickname
            elif path.endswith('/following'):
                sendJson = []
                sendJsonStr = 'masto API following sent for ' + nickname
            elif path.endswith('/statuses'):
                sendJson = []
                sendJsonStr = 'masto API statuses sent for ' + nickname
            elif path.endswith('/search'):
                sendJson = []
                sendJsonStr = 'masto API search sent ' + originalPath
            elif path.endswith('/relationships'):
                sendJson = []
                sendJsonStr = \
                    'masto API relationships sent ' + originalPath
            else:
                sendJson = \
                    _getMastoApiV1Account(baseDir, pathNickname, domain)
                sendJsonStr = 'masto API account sent for ' + nickname

    if path.startswith('/api/v1/blocks'):
        sendJson = []
        sendJsonStr = 'masto API instance blocks sent'
    elif path.startswith('/api/v1/favorites'):
        sendJson = []
        sendJsonStr = 'masto API favorites sent'
    elif path.startswith('/api/v1/follow_requests'):
        sendJson = []
        sendJsonStr = 'masto API follow requests sent'
    elif path.startswith('/api/v1/mutes'):
        sendJson = []
        sendJsonStr = 'masto API mutes sent'
    elif path.startswith('/api/v1/notifications'):
        sendJson = []
        sendJsonStr = 'masto API notifications sent'
    elif path.startswith('/api/v1/reports'):
        sendJson = []
        sendJsonStr = 'masto API reports sent'
    elif path.startswith('/api/v1/statuses'):
        sendJson = []
        sendJsonStr = 'masto API statuses sent'
    elif path.startswith('/api/v1/timelines'):
        sendJson = []
        sendJsonStr = 'masto API timelines sent'
    elif path.startswith('/api/v1/custom_emojis'):
        sendJson = customEmoji
        sendJsonStr = 'masto API custom emojis sent'

    adminNickname = getConfigParam(baseDir, 'admin')
    if adminNickname and path == '/api/v1/instance':
        instanceDescriptionShort = \
            getConfigParam(baseDir,
                           'instanceDescriptionShort')
        if not instanceDescriptionShort:
            instanceDescriptionShort = \
                translate['Yet another Epicyon Instance']
        instanceDescription = getConfigParam(baseDir,
                                             'instanceDescription')
        instanceTitle = getConfigParam(baseDir, 'instanceTitle')

        if callingDomain.endswith('.onion') and onionDomain:
            domainFull = onionDomain
            httpPrefix = 'http'
        elif (callingDomain.endswith('.i2p') and i2pDomain):
            domainFull = i2pDomain
            httpPrefix = 'http'

        if brochMode:
            showNodeInfoAccounts = False

        sendJson = \
            metaDataInstance(showNodeInfoAccounts,
                             instanceTitle,
                             instanceDescriptionShort,
                             instanceDescription,
                             httpPrefix,
                             baseDir,
                             adminNickname,
                             domain,
                             domainFull,
                             registration,
                             systemLanguage,
                             projectVersion)
        sendJsonStr = 'masto API instance metadata sent'
    elif path.startswith('/api/v1/instance/peers'):
        # This is just a dummy result.
        # Showing the full list of peers would have privacy implications.
        # On a large instance you are somewhat lost in the crowd, but on
        # small instances a full list of peers would convey a lot of
        # information about the interests of a small number of accounts
        sendJson = ['mastodon.social', domainFull]
        sendJsonStr = 'masto API peers metadata sent'
    elif path.startswith('/api/v1/instance/activity'):
        sendJson = []
        sendJsonStr = 'masto API activity metadata sent'
    return sendJson, sendJsonStr
