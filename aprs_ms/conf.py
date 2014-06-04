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

import os

from ConfigParser import SafeConfigParser


class Settings(object):
    def __init__(self):
        self.defaults = {'Shared': {'debug': False,
                                    'db': 'sqlite:///aprs-ms.db'},
                         'Collect': {'aprs_is_host': 'greece.aprs2.net',
                                     'aprs_is_port': 1314,
                                     'callsign': 'NOCALL'},
                         'IMAP': {'imap_port': '1134'}}
        for pairs in self.defaults.values():
            for key, value in pairs.iteritems():
                setattr(self, '_' + key, value)
    
    def __getattr__(self, name):
        try:
            value = object.__getattribute__(self, '_' + name.lower())
        except AttributeError:
            raise AttributeError('\'%s\' object has no attribute \'%s\'' % (self.__class__.__name__, name))
        if name.upper() == 'DEBUG':
            if type(value) == str:
                return value.lower() in ('true', 'yes', '1')
        elif name.upper() in ('APRS_IS_PORT', 'IMAP_PORT'):
            return int(value)
        return value

settings = Settings()

configParser = SafeConfigParser(defaults=dict([pair for pairs in settings.defaults.itervalues() for pair in pairs.items()]))
if configParser.read([f for f in ('aprs-ms.cfg', '/etc/aprs-ms.cfg', os.environ.get("APRS_MS_CONFIGURATION")) if f]):
    for section, pairs in settings.defaults.iteritems():
        for key, value in pairs.iteritems():
            setattr(settings, '_' + key, configParser.get(section, key))
