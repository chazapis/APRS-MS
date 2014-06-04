#!/usr/bin/env python

# Copyright (c) 2014, Antony Chazapis <chazapis@gmail.com>
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

import sys
import re
import socket

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DataError

from db import Message, engine
from utils import doHash
from conf import settings

def main():
    Session = sessionmaker(bind=engine)
    session = Session()

    r = re.compile('^(?P<sender>[\w-]+)>([^:]+)::(?P<recipient>[^:]+):(?P<body>[^{]*){?(.*)$')

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((settings.APRS_IS_HOST, settings.APRS_IS_PORT))
            s.sendall('user %s pass %s\n' % (settings.CALLSIGN, doHash(settings.CALLSIGN)))

            try:
                f = s.makefile()
                for l in f:
                    print l,
                    m = r.match(l)
                    if not m:
                        continue
                
                    sender = m.group('sender').strip()
                    recipient = m.group('recipient').strip()
                    body = m.group('body').strip()
                
                    session.add(Message(sender=sender, recipient=recipient, body=body))
                    try:
                        session.commit()
                    except DataError as e:
                        print 'ERROR:', e
            except KeyboardInterrupt:
                raise
            finally:
                f.close()
        except KeyboardInterrupt:
            break
        finally:
            s.shutdown(socket.SHUT_RDWR)
            s.close()

if __name__ == '__main__':
    main()
