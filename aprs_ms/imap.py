#!/usr/bin/env python

# Copyright (c) 2014, Antony Chazapis <chazapis@gmail.com>
# Copyright (c) 2010, Dav Glass <davglass@gmail.com>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import settings

from twisted.mail import imap4
from twisted.mail.smtp import rfc822date
from twisted.internet import reactor, defer, protocol
from twisted.cred import portal, checkers, credentials
from twisted.cred import error as credError
from zope.interface import implements
from cStringIO import StringIO
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from db import Message, engine
from utils import doHash
from conf import settings


# Based on: https://github.com/davglass/twimapd

class APRSMSIAccount(object):
    implements(imap4.IAccount)
    
    def __init__(self, cache):
        self.cache = cache
    
    def addMailbox(self, name, mbox):
        raise imap4.MailboxException('Not allowed')
    
    def create(self, pathspec):
        raise imap4.MailboxException('Not allowed')
    
    def select(self, name, rw=True):
        name = name.title()
        if name == 'Inbox' or name == 'Sent':
            return APRSMSIMailbox(name, self.cache)
        return None
    
    def delete(self, name):
        raise imap4.MailboxException('Not allowed')
    
    def rename(self, oldname, newname):
        raise imap4.MailboxException('Not allowed')
    
    def isSubscribed(self, name):
        return True
    
    def subscribe(self, name):
        return True
    
    def unsubscribe(self, path):
        return False
    
    def listMailboxes(self, ref, wildcard):
        return [('Inbox', APRSMSIMailbox('Inbox', self.cache)),
                ('Sent', APRSMSIMailbox('Sent', self.cache))]

class APRSMSIMailbox(object):
    implements(imap4.IMailbox)
    
    def __init__(self, folder, cache):
        self.folder = folder
        self.cache = cache
        self.username = self.cache['username']
        self.session = self.cache['session']
        self.listeners = []
    
    def getFlags(self):
        return ['\Seen', '\HasNoChildren']
    
    def getHierarchicalDelimiter(self):
        return '.'
    
    def getUIDValidity(self):
        if self.folder == 'Inbox':
            return 0
        elif self.folder == 'Sent':
            return 1
    
    def getUID(self, messageNum):
        messages = self.session.query(Message).order_by(Message.id.asc())[messageNum - 1: messageNum]
        if messages:
            return messages[0].id
        raise imap4.MailboxException('Message not found')
    
    def getUIDNext(self):
        if self.folder == 'Inbox':
            message = self.session.query(Message).filter_by(recipient=self.username).order_by(Message.id.desc()).first()
        elif self.folder == 'Sent':
            message = self.session.query(Message).filter_by(sender=self.username).order_by(Message.id.desc()).first()
        if message:
            return message.id + 1
        return 1
    
    def getMessageCount(self):
        if self.folder == 'Inbox':
            return self.session.query(Message).filter_by(recipient=self.username).count()
        elif self.folder == 'Sent':
            return self.session.query(Message).filter_by(sender=self.username).count()
    
    def getRecentCount(self):
        return self.getUnseenCount()
    
    def getUnseenCount(self):
        if self.folder == 'Inbox':
            return self.session.query(Message).filter_by(recipient=self.username, read=False).count()
        elif self.folder == 'Sent':
            return self.session.query(Message).filter_by(sender=self.username, read=False).count()
    
    def isWriteable(self):
        return True
    
    def destroy(self):
        raise imap4.MailboxException('Not allowed')
    
    def requestStatus(self, names):
        statusRequestDict = {'MESSAGES': 'getMessageCount',
                             'RECENT': 'getRecentCount',
                             'UIDNEXT': 'getUIDNext',
                             'UIDVALIDITY': 'getUIDValidity',
                             'UNSEEN': 'getUnseenCount'}
        s = {}
        for n in names:
            s[n] = getattr(self, statusRequestDict[n.upper()])()
        return s
    
    def addListener(self, listener):
        self.listeners.append(listener)
        return True
    
    def removeListener(self, listener):
        self.listeners.remove(listener)
        return True
    
    def addMessage(self, msg, flags=(), date=None):
        raise imap4.MailboxException('Not allowed')
    
    def expunge(self):
        raise imap4.MailboxException('Not allowed')
    
    def fetch(self, messages, uid):
        print 'FETCH %s %s' % (messages, uid)
        response = []
        if self.folder == 'Inbox':
            query = self.session.query(Message).filter(Message.recipient==self.username).order_by(Message.id.asc())
        elif self.folder == 'Sent':
            query = self.session.query(Message).filter(Message.sender==self.username).order_by(Message.id.asc())
        if uid:
            for low, high in messages.ranges:
                if low == high:
                    if low is None:
                        query = query.all()
                    else:
                        query = query.filter(Message.id==low)
                elif low is None:
                    query = query.filter(Message.id >= high)
                else:
                    query = query.filter(Message.id >= low, Message.id <= high)
                
                for message in query.order_by(Message.id.asc()):
                    response.append((message.id, APRSMSIMessage(message)))
        else:
            for low, high in messages.ranges:
                if low == high:
                    if low is None:
                        query = query.all()
                        sequence_number = 1
                    else:
                        query = query.all()[low - 1:low]
                        sequence_number = low
                elif low is None:
                    query = query.all()[high - 1:]
                    sequence_number = high
                else:
                    query = query.all()[low - 1:high]
                    sequence_number = low
                
                for message in query:
                    response.append((sequence_number, APRSMSIMessage(message)))
                    sequence_number += 1
        
        return response
    
    def store(self, messages, flags, mode, uid):
        print 'STORE %s %s %s %s' % (messages, flags, mode, uid)
        if self.folder == 'Inbox':
            query = self.session.query(Message).filter(Message.recipient==self.username)
        elif self.folder == 'Sent':
            query = self.session.query(Message).filter(Message.sender==self.username)
        if uid:
            for low, high in messages.ranges:
                if low == high:
                    if low is None:
                        pass
                    else:
                        query = query.filter(Message.id==low)
                elif low is None:
                    query = query.filter(Message.id >= high)
                else:
                    query = query.filter(Message.id >= low, Message.id <= high)
                
                if mode == -1:
                    query.update({'read': False})
                else:
                    query.update({'read': True})
        else:
            for low, high in messages.ranges:
                if low == high:
                    if low is None:
                        query = query.all()
                    else:
                        query = query.all()[low - 1:low]
                elif low is None:
                    query = query.all()[high - 1:]
                else:
                    query = query.all()[low - 1:high]
                
                for message in query:
                    if mode == -1:
                        message.read = False
                    else:
                        message.read = True
        
        self.session.commit()

class APRSMSIMessage(object):
    implements(imap4.IMessage)
    
    def __init__(self, message):
        self.message = message
    
    def getHeaders(self, negate, *names):
        headers = {'to': '%s <%s@aprs-ms.net>' % (self.message.recipient, self.message.recipient),
                   'envelope-to': '%s@twitter.com' % self.message.recipient,
                   'return-path': '%s@twitter.com' % self.message.sender,
                   'from': '%s <%s@twitter.com>' % (self.message.sender, self.message.sender),
                   'delivery-date': '%s' % self.getInternalDate(), 
                   'date': '%s' % self.getInternalDate(),
                   'subject': '%s' % self.message.body,
                   'message-id': '<%s@aprs-ms.net>' % self.message.id,
                   'content-type': 'text/plain; charset="UTF-8"',
                   'content-transfer-encoding': 'quoted-printable',
                   'mime-version': '1.0'}
        for i in headers:
            headers[i] = headers[i].encode('utf-8', 'replace')
        
        return headers
    
    def getBodyFile(self):
        return StringIO(self.message.body.encode('utf-8'))
    
    def getSize(self):
        return len(self.message.body)
    
    def isMultipart(self):
        return False
    
    def getSubPart(self, part):
        raise TypeError('Not a multipart message')
    
    def getUID(self):
        return self.message.id
    
    def getFlags(self):
        if self.message.read:
            return['\Seen']
        return []
    
    def getInternalDate(self):
        return rfc822date(self.message.timestamp.timetuple())

class APRSMSCredentialsChecker():
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword,)
    
    def __init__(self, cache):
        self.cache = cache
    
    def requestAvatarId(self, credentials):
#         if credentials.password != self.doHash(credentials.username):
#             return defer.fail(credError.UnauthorizedLogin('Bad passcode'))
        
        self.cache['username'] = credentials.username
        
        Session = sessionmaker(bind=engine)
        session = Session()
        self.cache['session'] = session
        
        return defer.succeed(credentials.username)

class MailUserRealm(object):
    implements(portal.IRealm)
    
    def __init__(self, cache):
        self.cache = cache
    
    def requestAvatar(self, avatarId, mind, *interfaces):
        for requestedInterface in interfaces:
            if requestedInterface == imap4.IAccount:
                return (requestedInterface, APRSMSIAccount(self.cache), lambda: None)

        raise KeyError('None of the requested interfaces is supported')

class IMAPServerProtocol(imap4.IMAP4Server):
    'Subclass of imap4.IMAP4Server that adds debugging.'
    
    def lineReceived(self, line):
        if settings.DEBUG:
            print 'CLIENT:', line
        imap4.IMAP4Server.lineReceived(self, line)
    
    def sendLine(self, line):
        imap4.IMAP4Server.sendLine(self, line)
        if settings.DEBUG:
            print 'SERVER:', line

class IMAPFactory(protocol.Factory):
    portal = None

    def buildProtocol(self, address):
        p = IMAPServerProtocol()
        p.portal = self.portal
        return p

def main():
    cache = {}
    
    portal = portal.Portal(MailUserRealm(cache))
    portal.registerChecker(APRSMSCredentialsChecker(cache))
    
    factory = IMAPFactory()
    factory.portal = portal
    
    reactor.listenTCP(settings.IMAP_PORT, factory)
    reactor.run()

if __name__ == '__main__':
    main()
