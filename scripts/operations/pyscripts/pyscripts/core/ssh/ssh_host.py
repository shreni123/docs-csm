#
# MIT License
#
# (C) Copyright 2022 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#

import getpass

class SshHost:
    """
    Maintains details about an SSH Host.
    """

    def __init__(self, hostname, username, rawdata = None, domain_suffix = None):
        if rawdata:
            self.parent = rawdata["Parent"]
            self.xname = rawdata["Xname"]
            self.type = rawdata["Type"]
            self.clazz = rawdata["Class"]
            self.type_string = rawdata["TypeString"]
            self.last_updated = rawdata["LastUpdated"]
            self.last_updated_time = rawdata["LastUpdatedTime"]
            self.rawdata = rawdata;

        self.hostname = hostname
        self.username = username
        self.password = None
        self.state = None
        self.no_password_needed = False
        self.domain_suffix = domain_suffix
        self.original_host = None

    def get_password(self, reset_cached = False):
        password = self.password
        no_password_needed = self.no_password_needed
        if self.original_host:
            password = self.original_host.password
            no_password_needed = self.original_host.no_password_needed

        if reset_cached or (not password and not no_password_needed):
            password = getpass.getpass('%s password (leave blank and hit Enter if not using password): ' % self.hostname)

            if self.original_host:
                self.original_host.password = password

                if not password:
                    self.original_host.no_password_needed = True
            else:
                self.password = password

                if not password:
                    self.no_password_needed = True

        return password

    def with_domain_suffix(self, domain_suffix):
        newHost = SshHost(self.hostname, self.username, self.rawdata, domain_suffix)
        newHost.original_host = self if not self.original_host else self.original_host
        return newHost

    def get_state(self):
        if self.original_host:
            return self.original_host.state
        else:
            return self.state

    def set_state(self, state):
        if self.original_host:
            self.original_host.state = state
        else:
            self.state = state

    def is_ready(self):
        state = self.get_state()
        return state == "Configured" or state == "Ready" or state == None # if None, state is unknown, so we'll assume it is ready

    def get_full_domain_name(self):
        if self.domain_suffix:
            return "{}.{}".format(self.hostname, self.domain_suffix)
        else:
            return self.hostname
