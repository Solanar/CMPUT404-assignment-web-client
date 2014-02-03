#!/usr/bin/env python
# Copyright 2014 Abram Hindle, Andrew Charles
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
#import re  # or not
import time
# you may use urllib to encode data appropriately
import urllib


def help():
    print "httpclient.py [GET/POST] [URL]\n"


class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        # use sockets!
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print 'Failed to create socket'
            sys.exit()
        #print 'Socket Created'

        s.connect((host, port))
        #print 'Socket Connected to ' + host + ' at ' + str(port)

        return s

    def get_code(self, data):
        return data.split()[1]

    def get_headers(self, data):
        return data

    def get_body(self, data):
        return data

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        r = self.sendmsg(url, 'GET', args)
        t = r.split("\r\n\r\n")
        c = self.get_code(t[0])
        b = self.get_body(t[1])
        code = int(c)
        body = b
        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        r = self.sendmsg(url, 'POST', args)
        t = r.split("\r\n\r\n")
        c = self.get_code(t[0])
        #h = self.get_headers(t[0])
        b = self.get_body(t[1])
        code = int(c)
        body = b
        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

    def parse_url(self, url, post=False):
        if url.startswith('http://'):
            url = url[len('http://'):]

        args = ''
        if post and '?' in url:
            tmp = url.split('?')
            args = tmp[1]
            url = tmp[0]

        host = ''
        i = 0
        while i < len(url):
            if url[i] is '/' or url[i] is ':':
                break
            host += url[i]
            i += 1

        port = '80'
        if i < len(url) and url[i] is ':':
            port = ''
            while i < len(url):
                if url[i] is '/':
                    break
                if url[i] is not ':':
                    port += url[i]
                i += 1

        path = ''
        while i < len(url):
            path += url[i]
            i += 1

        return (host, int(port), path, args)

    def sendmsg(self, url, option, args=None):
        if option is 'POST':
            post = True
        else:
            post = False
        host, port, path, uargs = self.parse_url(url, post)
        if args is None:
            args = uargs
        s = self.connect(host, port)
        msg = option + ' ' + path + " HTTP/1.1\r\n"
        msg += 'Host: ' + host + "\r\n"
        if args is not None:
            msg += "Content-Type: application/x-www-form-urlencoded\r\n"
            enc_args = urllib.urlencode(args)
            msg += 'Content-Length: ' + str(len(enc_args)) + "\r\n"
            msg += "\r\n"
            msg += enc_args
        else:
            msg += "\r\n"
        s.sendall(msg)
        time.sleep(1)
        r = self.recvall(s)
        s.close()
        return r


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command(sys.argv[2], sys.argv[1])
    else:
        print client.command(command, sys.argv[1])
